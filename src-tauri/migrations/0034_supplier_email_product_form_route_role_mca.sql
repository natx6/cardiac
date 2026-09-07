-- Supplier email (captured on the supplier form; shown on the printed
-- purchase order and the stock detail view).
ALTER TABLE suppliers ADD COLUMN email TEXT;
-- Product dosage form (tablet/syrup/...) + administration route
-- (oral/topical/...) — captured on Add Product alongside unit, shown on
-- cards, cart lines and receipts.
ALTER TABLE products ADD COLUMN dosage_form TEXT;
ALTER TABLE products ADD COLUMN route TEXT;
-- Roles move to owner/manager/mca: existing worker accounts become mca.
UPDATE users SET role = 'mca' WHERE role = 'worker';
