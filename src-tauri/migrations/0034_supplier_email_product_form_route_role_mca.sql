-- Supplier email (captured on the supplier form; shown on the printed
-- purchase order and the stock detail view).
ALTER TABLE suppliers ADD COLUMN email TEXT;
-- Product dosage form (tablet/syrup/...) + administration route
-- (oral/topical/...) — captured on Add Product alongside unit, shown on
-- cards, cart lines and receipts.
ALTER TABLE products ADD COLUMN dosage_form TEXT;
ALTER TABLE products ADD COLUMN route TEXT;
-- Role rewrite worker->mca lives in 0035 (table rebuild): an in-place UPDATE
-- here would violate the old users CHECK constraint on existing databases.
