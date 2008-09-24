ALTER TABLE "info_extendedinfo" ADD COLUMN "grad_student" boolean;
UPDATE "info_extendedinfo" set grad_student = False;
ALTER TABLE "info_extendedinfo" ALTER COLUMN "grad_student" SET NOT NULL;
