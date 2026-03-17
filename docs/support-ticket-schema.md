# Support Ticket Schema Contract

The support module added in this repo expects the following database tables and columns.

## `support_tickets`

Required columns:

- `id` UUID primary key
- `ticket_number` text unique not null
- `user_id` UUID not null references `users(id)`
- `user_role` text not null
- `category` text not null
- `priority` text not null
- `subject` text not null
- `description` text not null
- `status` text not null
- `assigned_admin_email` text null
- `resolution_summary` text null
- `created_at` timestamp not null default current timestamp
- `updated_at` timestamp not null default current timestamp
- `resolved_at` timestamp null
- `closed_at` timestamp null

Suggested status values:

- `open`
- `in_progress`
- `waiting_for_user`
- `resolved`
- `closed`

Suggested priority values:

- `low`
- `medium`
- `high`
- `urgent`

Suggested category values:

- `account`
- `orders`
- `payments`
- `products`
- `delivery`
- `verification`
- `technical`
- `other`

## `support_ticket_messages`

Required columns:

- `id` UUID primary key
- `ticket_id` UUID not null references `support_tickets(id)`
- `sender_type` text not null
- `sender_user_id` UUID null references `users(id)`
- `sender_name` text null
- `message` text not null
- `is_internal_note` boolean not null default false
- `created_at` timestamp not null default current timestamp

Suggested sender types:

- `user`
- `admin`

## API expectations

The backend implementation assumes:

- one opening message is stored in `support_ticket_messages` when a ticket is created
- `updated_at` changes whenever a ticket gets a reply, assignment, or status change
- admin assignment is stored in `assigned_admin_email`
- admin resolution notes can be stored in `resolution_summary`

## Implemented endpoints

- `POST /api/support/tickets`
- `GET /api/support/tickets/my/<firebase_uid>`
- `GET /api/support/tickets/<ticket_id>?firebase_uid=<uid>`
- `POST /api/support/tickets/<ticket_id>/messages`
- `GET /api/support/admin/stats`
- `GET /api/support/admin/tickets`
- `GET /api/support/admin/tickets/<ticket_id>`
- `POST /api/support/admin/tickets/<ticket_id>/messages`
- `PATCH /api/support/admin/tickets/<ticket_id>/status`
- `PATCH /api/support/admin/tickets/<ticket_id>/assign`
