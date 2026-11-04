# API walkthrough

End-to-end example against a freshly seeded database. The API is available at
`http://localhost:8000`; swap the base URL for your deployment.

```bash
API=http://localhost:8000/api/v1
```

## 1. Sign in

```bash
TOKEN=$(curl -s -X POST "$API/auth/login" \
  -d "username=librarian@library.dev&password=library12345" | jq -r .access_token)

AUTH="Authorization: Bearer $TOKEN"
```

## 2. Inspect the catalogue

```bash
curl -s "$API/books?q=rayuela&available=true" | jq
curl -s "$API/books?sort=publication_year&order=desc&page=1&size=5" | jq
curl -s "$API/books/1" | jq '{title, authors: [.authors[].name], copies: .total_copies}'
```

## 3. Register a member

```bash
curl -s -X POST "$API/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"reader@example.com","password":"password123","full_name":"New Reader"}' | jq
```

## 4. Add a title and a physical copy

```bash
AUTHOR_ID=$(curl -s -X POST "$API/authors" -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"name":"Ursula K. Le Guin","birth_year":1929}' | jq -r .id)

BOOK_ID=$(curl -s -X POST "$API/books" -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"isbn\":\"9780547773742\",\"title\":\"The Dispossessed\",\"author_ids\":[$AUTHOR_ID],\"publication_year\":1974}" | jq -r .id)

BRANCH_ID=$(curl -s "$API/branches" | jq -r '.items[0].id')

curl -s -X POST "$API/books/$BOOK_ID/copies" -H "$AUTH" -H "Content-Type: application/json" \
  -d "{\"book_id\":$BOOK_ID,\"branch_id\":$BRANCH_ID,\"inventory_code\":\"BC-9001\"}" | jq
```

## 5. Borrow a book

```bash
MEMBER_TOKEN=$(curl -s -X POST "$API/auth/login" \
  -d "username=member@library.dev&password=library12345" | jq -r .access_token)

LOAN_ID=$(curl -s -X POST "$API/loans" \
  -H "Authorization: Bearer $MEMBER_TOKEN" -H "Content-Type: application/json" \
  -d "{\"book_id\":$BOOK_ID}" | jq -r .id)

curl -s "$API/loans/$LOAN_ID" -H "Authorization: Bearer $MEMBER_TOKEN" | jq '{status, due_date}'
```

## 6. Renew or return

```bash
curl -s -X POST "$API/loans/$LOAN_ID/renew" -H "Authorization: Bearer $MEMBER_TOKEN" | jq .renewals
curl -s -X POST "$API/loans/$LOAN_ID/return" -H "Authorization: Bearer $MEMBER_TOKEN" | jq .status
```

A late return creates a fine automatically:

```bash
curl -s "$API/fines" -H "Authorization: Bearer $MEMBER_TOKEN" | jq '.items[] | {amount, status}'
```

## 7. Reserve a title with no available copies

```bash
curl -s -X POST "$API/reservations" \
  -H "Authorization: Bearer $MEMBER_TOKEN" -H "Content-Type: application/json" \
  -d "{\"book_id\":$BOOK_ID}" | jq '{status, queue_position: .id}'
```

## 8. Staff operations

```bash
# Flag overdue loans
curl -s -X POST "$API/loans/overdue/refresh" -H "$AUTH" | jq

# Release expired holds
curl -s -X POST "$API/reservations/expire" -H "$AUTH" | jq

# Mark a fine as paid
curl -s -X POST "$API/fines/1/pay" -H "$AUTH" | jq .status
```

## Error format

All errors use RFC 7807 (`application/problem+json`):

```json
{
  "type": "about:blank",
  "title": "No copies available",
  "status": 409,
  "detail": "There are no available copies of 'Rayuela'.",
  "instance": "/api/v1/loans",
  "code": "no_copies_available"
}
```
