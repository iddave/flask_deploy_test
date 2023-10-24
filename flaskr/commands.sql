ALTER TABLE "QTable_temp" ALTER COLUMN id SET NOT NULL;
ALTER TABLE "QTable_temp" ALTER COLUMN id DROP DEFAULT;
ALTER TABLE "QTable_temp" ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;

SELECT column_name, is_identity
FROM information_schema.columns
WHERE table_name = 'QTable_temp' AND column_name = 'id';
