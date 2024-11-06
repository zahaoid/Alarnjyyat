CREATE TABLE "public"."corrections" ( 
  "entryid" INTEGER NOT NULL,
  "correction" VARCHAR(32) NOT NULL,
  CONSTRAINT "corrections_pkey" PRIMARY KEY ("entryid", "correction")
);
CREATE TABLE "public"."entries" ( 
  "id" SERIAL,
  "origin" CHARACTER(2) NOT NULL,
  "original" VARCHAR(64) NOT NULL,
  "translationese" VARCHAR(64) NOT NULL,
  "timestamp" TIMESTAMP NOT NULL DEFAULT now() ,
  "submitter" VARCHAR(64) NULL,
  "approvedby" VARCHAR(64) NULL,
  CONSTRAINT "entries_pkey" PRIMARY KEY ("id")
);
CREATE TABLE "public"."users" ( 
  "username" VARCHAR(64) NOT NULL,
  "email" VARCHAR(128) NOT NULL,
  "passwordhash" VARCHAR(256) NOT NULL,
  "registeredat" TIMESTAMP NOT NULL DEFAULT now() ,
  "isadmin" BOOLEAN NOT NULL DEFAULT false ,
  CONSTRAINT "users_pkey" PRIMARY KEY ("username"),
  CONSTRAINT "users_email_key" UNIQUE ("email")
);
ALTER TABLE "public"."corrections" DISABLE TRIGGER ALL;
ALTER TABLE "public"."entries" DISABLE TRIGGER ALL;
ALTER TABLE "public"."users" DISABLE TRIGGER ALL;
ALTER TABLE "public"."corrections" ENABLE TRIGGER ALL;
ALTER TABLE "public"."entries" ENABLE TRIGGER ALL;
ALTER TABLE "public"."users" ENABLE TRIGGER ALL;
ALTER TABLE "public"."corrections" ADD CONSTRAINT "corrections_entryid_fkey" FOREIGN KEY ("entryid") REFERENCES "public"."entries" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."entries" ADD CONSTRAINT "entries_approvedby_fkey" FOREIGN KEY ("approvedby") REFERENCES "public"."users" ("username") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "public"."entries" ADD CONSTRAINT "entries_submitter_fkey" FOREIGN KEY ("submitter") REFERENCES "public"."users" ("username") ON DELETE NO ACTION ON UPDATE NO ACTION;