-- car-finder-il :: seen_listings
-- Remembers which listings were already pushed, so the scheduled run only ever
-- pings on genuinely NEW matches or real price drops.
--
-- Apply with either:
--   supabase db push                          (if you keep this under supabase/migrations/)
--   psql "$DATABASE_URL" -f db/seen_listings.sql
--   or paste into the Supabase SQL editor.

create table if not exists public.seen_listings (
  criteria_id text        not null,
  listing_id  text        not null,
  source      text        not null default 'yad2',
  title       text,
  url         text,
  price       integer,
  last_price  integer,
  score       integer,
  first_seen  timestamptz not null default now(),
  last_seen   timestamptz not null default now(),
  primary key (criteria_id, listing_id)
);

create index if not exists seen_listings_last_seen_idx
  on public.seen_listings (last_seen desc);

-- Locked down: only the service_role key (used by the cron) reads/writes this.
-- The publishable/anon key gets nothing here.
alter table public.seen_listings enable row level security;
