ALTER TABLE "info_extendedinfo" ADD COLUMN "aim_sn" varchar(30) NULL;
ALTER TABLE "cand_candidateapplication" ALTER COLUMN "entry_id" DROP NOT NULL;
ALTER TABLE "cand_candidateapplication" ADD COLUMN "release_information" boolean;
