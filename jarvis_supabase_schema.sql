-- 1. Ativar a extensão de Vetores (Memória da IA)
create extension if not exists vector;

-- 2. Tabela de Perfis Públicos (Ligada à autenticação do Supabase)
create table public.profiles (
  id uuid references auth.users on delete cascade not null primary key,
  name text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
-- Habilita segurança em nível de linha (apenas o dono vê seu perfil)
alter table public.profiles enable row level security;
create policy "Users can view own profile" on profiles for select using (auth.uid() = id);
create policy "Users can update own profile" on profiles for update using (auth.uid() = id);

-- 3. Tabela de Dispositivos (Seus computadores)
create table public.devices (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  device_name text not null,
  is_online boolean default false,
  last_seen timestamp with time zone default timezone('utc'::text, now()) not null
);
alter table public.devices enable row level security;
create policy "Users can manage their own devices" on devices for all using (auth.uid() = user_id);

-- 4. Tabela de Comandos Remotos (O "Correio" entre Site e PC)
create table public.device_commands (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  target_device_id uuid references public.devices(id) on delete cascade,
  command_type text not null, -- Ex: 'OPEN_APP'
  payload jsonb default '{}'::jsonb, -- Ex: {"app": "spotify"}
  status text default 'PENDING', -- PENDING, EXECUTED, FAILED
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
alter table public.device_commands enable row level security;
create policy "Users can manage their own commands" on device_commands for all using (auth.uid() = user_id);

-- 5. Tabela de Memória da IA (Mensagens e Vetores)
-- Substitua '1536' pelo tamanho do vetor do modelo que for usar (o text-embedding-ada-002 ou gemini costuma usar 1536 ou 768).
create table public.messages (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  role text not null, -- 'user', 'assistant', 'system'
  content text not null,
  embedding vector(768), -- Exemplo com vetor de 768 dimensões (ajuste conforme a API)
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
alter table public.messages enable row level security;
create policy "Users can manage their own messages" on messages for all using (auth.uid() = user_id);

-- 6. Habilitar o modo Real-Time para que o PC receba notificações instantâneas
-- do Supabase quando houver um novo comando.
alter publication supabase_realtime add table devices;
alter publication supabase_realtime add table device_commands;

-- 7. Trigger para criar perfil automaticamente quando um usuário se registrar
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, name)
  values (new.id, new.raw_user_meta_data->>'full_name');
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
