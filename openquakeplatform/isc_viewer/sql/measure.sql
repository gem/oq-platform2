CREATE TABLE "isc_viewer_measure" (
    "id" serial NOT NULL PRIMARY KEY,
    "the_geom" geometry,
    "src_id" integer NOT NULL,
    "date" timestamp with time zone NOT NULL,
    "lat" double precision NOT NULL,
    "lon" double precision NOT NULL,
    "smajax" double precision,
    "sminax" double precision,
    "strike" double precision,
    "epic_q" varchar(1) NOT NULL,
    "depth" double precision,
    "depth_unc" double precision,
    "depth_q" varchar(1) NOT NULL,
    "mw" double precision,
    "mw_unc" double precision,
    "mw_q" varchar(1) NOT NULL,
    "s" varchar(1) NOT NULL,
    "mo" double precision,
    "fac" double precision,
    "mo_auth" varchar(255) NOT NULL,
    "mpp" double precision,
    "mpr" double precision,
    "mrr" double precision,
    "mrt" double precision,
    "mtp" double precision,
    "mtt" double precision,
    "eventid" integer NOT NULL,
    CONSTRAINT enforce_dims_the_geom CHECK ((st_ndims(the_geom) = 2)),
    CONSTRAINT enforce_geotype_the_geom CHECK (((geometrytype(the_geom) = 'POINT'::text) OR (the_geom IS NULL))),
    CONSTRAINT enforce_srid_the_geom CHECK ((st_srid(the_geom) = 4326))
)
;