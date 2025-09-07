--
-- PostgreSQL database dump
--

-- Dumped from database version 13.10
-- Dumped by pg_dump version 13.10

-- Started on 2025-09-06 21:31:17

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 200 (class 1259 OID 321694)
-- Name: uploaded_file; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.uploaded_file (
    id bigint NOT NULL,
    file character varying(100) NOT NULL,
    uploaded_at timestamp with time zone NOT NULL,
    analysis text,
    review_id bigint NOT NULL,
    description text,
    file_type_id bigint
);


ALTER TABLE public.uploaded_file OWNER TO postgres;

--
-- TOC entry 201 (class 1259 OID 321700)
-- Name: CaDQM_backend_uploadedfile_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."CaDQM_backend_uploadedfile_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."CaDQM_backend_uploadedfile_id_seq" OWNER TO postgres;

--
-- TOC entry 3754 (class 0 OID 0)
-- Dependencies: 201
-- Name: CaDQM_backend_uploadedfile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."CaDQM_backend_uploadedfile_id_seq" OWNED BY public.uploaded_file.id;


--
-- TOC entry 202 (class 1259 OID 321702)
-- Name: application_domain; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.application_domain (
    contextcomponent_ptr_id bigint NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.application_domain OWNER TO postgres;

--
-- TOC entry 203 (class 1259 OID 321708)
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO postgres;

--
-- TOC entry 204 (class 1259 OID 321711)
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO postgres;

--
-- TOC entry 3755 (class 0 OID 0)
-- Dependencies: 204
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- TOC entry 205 (class 1259 OID 321713)
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO postgres;

--
-- TOC entry 206 (class 1259 OID 321716)
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO postgres;

--
-- TOC entry 3756 (class 0 OID 0)
-- Dependencies: 206
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- TOC entry 207 (class 1259 OID 321718)
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO postgres;

--
-- TOC entry 208 (class 1259 OID 321721)
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO postgres;

--
-- TOC entry 3757 (class 0 OID 0)
-- Dependencies: 208
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- TOC entry 209 (class 1259 OID 321723)
-- Name: business_rule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.business_rule (
    contextcomponent_ptr_id bigint NOT NULL,
    statement text NOT NULL,
    semantic text NOT NULL
);


ALTER TABLE public.business_rule OWNER TO postgres;

--
-- TOC entry 210 (class 1259 OID 321729)
-- Name: context; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.context (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    version character varying(50) NOT NULL,
    previous_version_id bigint
);


ALTER TABLE public.context OWNER TO postgres;

--
-- TOC entry 211 (class 1259 OID 321732)
-- Name: context_component; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.context_component (
    id bigint NOT NULL,
    project_stage_id bigint
);


ALTER TABLE public.context_component OWNER TO postgres;

--
-- TOC entry 212 (class 1259 OID 321735)
-- Name: context_component_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.context_component_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.context_component_id_seq OWNER TO postgres;

--
-- TOC entry 3758 (class 0 OID 0)
-- Dependencies: 212
-- Name: context_component_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.context_component_id_seq OWNED BY public.context_component.id;


--
-- TOC entry 213 (class 1259 OID 321737)
-- Name: context_context_components; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.context_context_components (
    id integer NOT NULL,
    context_id bigint NOT NULL,
    contextcomponent_id bigint NOT NULL
);


ALTER TABLE public.context_context_components OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 321740)
-- Name: context_context_components_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.context_context_components_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.context_context_components_id_seq OWNER TO postgres;

--
-- TOC entry 3759 (class 0 OID 0)
-- Dependencies: 214
-- Name: context_context_components_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.context_context_components_id_seq OWNED BY public.context_context_components.id;


--
-- TOC entry 215 (class 1259 OID 321742)
-- Name: context_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.context_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.context_id_seq OWNER TO postgres;

--
-- TOC entry 3760 (class 0 OID 0)
-- Dependencies: 215
-- Name: context_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.context_id_seq OWNED BY public.context.id;


--
-- TOC entry 216 (class 1259 OID 321744)
-- Name: data_at_hand; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_at_hand (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    date date NOT NULL,
    url_db character varying(255) NOT NULL,
    user_db character varying(255) NOT NULL,
    pass_db character varying(255) NOT NULL,
    port integer,
    type character varying(50)
);


ALTER TABLE public.data_at_hand OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 321750)
-- Name: data_at_hand_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_at_hand_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.data_at_hand_id_seq OWNER TO postgres;

--
-- TOC entry 3761 (class 0 OID 0)
-- Dependencies: 217
-- Name: data_at_hand_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_at_hand_id_seq OWNED BY public.data_at_hand.id;


--
-- TOC entry 218 (class 1259 OID 321752)
-- Name: data_filtering; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_filtering (
    contextcomponent_ptr_id bigint NOT NULL,
    statement text NOT NULL,
    description text NOT NULL,
    task_at_hand_id bigint
);


ALTER TABLE public.data_filtering OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 321758)
-- Name: data_profiling; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_profiling (
    id bigint NOT NULL,
    description text NOT NULL,
    type character varying(50) NOT NULL,
    result jsonb NOT NULL,
    date timestamp with time zone NOT NULL,
    project_id bigint NOT NULL
);


ALTER TABLE public.data_profiling OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 321764)
-- Name: data_profiling_context_components; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_profiling_context_components (
    id integer NOT NULL,
    dataprofiling_id bigint NOT NULL,
    contextcomponent_id bigint NOT NULL
);


ALTER TABLE public.data_profiling_context_components OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 321767)
-- Name: data_profiling_context_components_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_profiling_context_components_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.data_profiling_context_components_id_seq OWNER TO postgres;

--
-- TOC entry 3762 (class 0 OID 0)
-- Dependencies: 221
-- Name: data_profiling_context_components_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_profiling_context_components_id_seq OWNED BY public.data_profiling_context_components.id;


--
-- TOC entry 222 (class 1259 OID 321769)
-- Name: data_profiling_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_profiling_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.data_profiling_id_seq OWNER TO postgres;

--
-- TOC entry 3763 (class 0 OID 0)
-- Dependencies: 222
-- Name: data_profiling_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_profiling_id_seq OWNED BY public.data_profiling.id;


--
-- TOC entry 223 (class 1259 OID 321771)
-- Name: data_schema; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_schema (
    id bigint NOT NULL,
    data_at_hand_id bigint NOT NULL,
    schema jsonb NOT NULL
);


ALTER TABLE public.data_schema OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 321777)
-- Name: data_schema_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_schema_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.data_schema_id_seq OWNER TO postgres;

--
-- TOC entry 3764 (class 0 OID 0)
-- Dependencies: 224
-- Name: data_schema_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_schema_id_seq OWNED BY public.data_schema.id;


--
-- TOC entry 225 (class 1259 OID 321779)
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id bigint NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 321786)
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO postgres;

--
-- TOC entry 3765 (class 0 OID 0)
-- Dependencies: 226
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- TOC entry 227 (class 1259 OID 321788)
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 321791)
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO postgres;

--
-- TOC entry 3766 (class 0 OID 0)
-- Dependencies: 228
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- TOC entry 229 (class 1259 OID 321793)
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 321799)
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO postgres;

--
-- TOC entry 3767 (class 0 OID 0)
-- Dependencies: 230
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- TOC entry 231 (class 1259 OID 321801)
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 321807)
-- Name: dq_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dq_metadata (
    contextcomponent_ptr_id bigint NOT NULL,
    path character varying(255) NOT NULL,
    description text NOT NULL,
    measurement text NOT NULL
);


ALTER TABLE public.dq_metadata OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 321813)
-- Name: dqmodel_dqmodel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_dqmodel (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    version character varying(20),
    created_at timestamp with time zone NOT NULL,
    previous_version_id bigint,
    finished_at timestamp with time zone,
    status character varying(10) NOT NULL
);


ALTER TABLE public.dqmodel_dqmodel OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 321816)
-- Name: dq_model_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dq_model_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dq_model_id_seq OWNER TO postgres;

--
-- TOC entry 3768 (class 0 OID 0)
-- Dependencies: 234
-- Name: dq_model_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dq_model_id_seq OWNED BY public.dqmodel_dqmodel.id;


--
-- TOC entry 235 (class 1259 OID 321818)
-- Name: dq_requirement; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dq_requirement (
    contextcomponent_ptr_id bigint NOT NULL,
    statement text NOT NULL,
    description text NOT NULL,
    user_type_id bigint
);


ALTER TABLE public.dq_requirement OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 321824)
-- Name: dq_requirement_data_filtering; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dq_requirement_data_filtering (
    id integer NOT NULL,
    dqrequirement_id bigint NOT NULL,
    datafiltering_id bigint NOT NULL
);


ALTER TABLE public.dq_requirement_data_filtering OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 321827)
-- Name: dq_requirement_data_filtering_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dq_requirement_data_filtering_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dq_requirement_data_filtering_id_seq OWNER TO postgres;

--
-- TOC entry 3769 (class 0 OID 0)
-- Dependencies: 237
-- Name: dq_requirement_data_filtering_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dq_requirement_data_filtering_id_seq OWNED BY public.dq_requirement_data_filtering.id;


--
-- TOC entry 238 (class 1259 OID 321829)
-- Name: dqmodel_aggregationdqmethod; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_aggregationdqmethod (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    algorithm text NOT NULL,
    "appliedTo" jsonb NOT NULL,
    "associatedTo_id" bigint NOT NULL
);


ALTER TABLE public.dqmodel_aggregationdqmethod OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 321835)
-- Name: dqmodel_aggregationdqmethod_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dqmodel_aggregationdqmethod_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dqmodel_aggregationdqmethod_id_seq OWNER TO postgres;

--
-- TOC entry 3770 (class 0 OID 0)
-- Dependencies: 239
-- Name: dqmodel_aggregationdqmethod_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dqmodel_aggregationdqmethod_id_seq OWNED BY public.dqmodel_aggregationdqmethod.id;


--
-- TOC entry 240 (class 1259 OID 321837)
-- Name: dqmodel_dqdimensionbase; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_dqdimensionbase (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    semantic text NOT NULL,
    is_disabled boolean NOT NULL
);


ALTER TABLE public.dqmodel_dqdimensionbase OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 321843)
-- Name: dqmodel_dqdimensionbase_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dqmodel_dqdimensionbase_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dqmodel_dqdimensionbase_id_seq OWNER TO postgres;

--
-- TOC entry 3771 (class 0 OID 0)
-- Dependencies: 241
-- Name: dqmodel_dqdimensionbase_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dqmodel_dqdimensionbase_id_seq OWNED BY public.dqmodel_dqdimensionbase.id;


--
-- TOC entry 242 (class 1259 OID 321845)
-- Name: dqmodel_dqfactorbase; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_dqfactorbase (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    semantic text NOT NULL,
    is_disabled boolean NOT NULL,
    "facetOf_id" bigint
);


ALTER TABLE public.dqmodel_dqfactorbase OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 321851)
-- Name: dqmodel_dqfactorbase_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dqmodel_dqfactorbase_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dqmodel_dqfactorbase_id_seq OWNER TO postgres;

--
-- TOC entry 3772 (class 0 OID 0)
-- Dependencies: 243
-- Name: dqmodel_dqfactorbase_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dqmodel_dqfactorbase_id_seq OWNED BY public.dqmodel_dqfactorbase.id;


--
-- TOC entry 244 (class 1259 OID 321853)
-- Name: dqmodel_dqmethodbase; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_dqmethodbase (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    "inputDataType" character varying(100) NOT NULL,
    "outputDataType" character varying(100) NOT NULL,
    algorithm text NOT NULL,
    is_disabled boolean NOT NULL,
    implements_id bigint
);


ALTER TABLE public.dqmodel_dqmethodbase OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 321859)
-- Name: dqmodel_dqmethodbase_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dqmodel_dqmethodbase_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dqmodel_dqmethodbase_id_seq OWNER TO postgres;

--
-- TOC entry 3773 (class 0 OID 0)
-- Dependencies: 245
-- Name: dqmodel_dqmethodbase_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dqmodel_dqmethodbase_id_seq OWNED BY public.dqmodel_dqmethodbase.id;


--
-- TOC entry 246 (class 1259 OID 321861)
-- Name: dqmodel_dqmetricbase; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_dqmetricbase (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    purpose text NOT NULL,
    granularity character varying(100) NOT NULL,
    "resultDomain" character varying(100) NOT NULL,
    is_disabled boolean NOT NULL,
    measures_id bigint
);


ALTER TABLE public.dqmodel_dqmetricbase OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 321867)
-- Name: dqmodel_dqmetricbase_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dqmodel_dqmetricbase_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dqmodel_dqmetricbase_id_seq OWNER TO postgres;

--
-- TOC entry 3774 (class 0 OID 0)
-- Dependencies: 247
-- Name: dqmodel_dqmetricbase_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dqmodel_dqmetricbase_id_seq OWNED BY public.dqmodel_dqmetricbase.id;


--
-- TOC entry 248 (class 1259 OID 321869)
-- Name: dqmodel_dqmodeldimension; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_dqmodeldimension (
    id bigint NOT NULL,
    context_components jsonb NOT NULL,
    dq_problems jsonb NOT NULL,
    dimension_base_id bigint NOT NULL,
    dq_model_id bigint NOT NULL
);


ALTER TABLE public.dqmodel_dqmodeldimension OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 321875)
-- Name: dqmodel_dqmodeldimension_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dqmodel_dqmodeldimension_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dqmodel_dqmodeldimension_id_seq OWNER TO postgres;

--
-- TOC entry 3775 (class 0 OID 0)
-- Dependencies: 249
-- Name: dqmodel_dqmodeldimension_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dqmodel_dqmodeldimension_id_seq OWNED BY public.dqmodel_dqmodeldimension.id;


--
-- TOC entry 250 (class 1259 OID 321877)
-- Name: dqmodel_dqmodelfactor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_dqmodelfactor (
    id bigint NOT NULL,
    context_components jsonb NOT NULL,
    dq_problems jsonb NOT NULL,
    dimension_id bigint,
    dq_model_id bigint NOT NULL,
    factor_base_id bigint NOT NULL
);


ALTER TABLE public.dqmodel_dqmodelfactor OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 321883)
-- Name: dqmodel_dqmodelfactor_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dqmodel_dqmodelfactor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dqmodel_dqmodelfactor_id_seq OWNER TO postgres;

--
-- TOC entry 3776 (class 0 OID 0)
-- Dependencies: 251
-- Name: dqmodel_dqmodelfactor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dqmodel_dqmodelfactor_id_seq OWNED BY public.dqmodel_dqmodelfactor.id;


--
-- TOC entry 252 (class 1259 OID 321885)
-- Name: dqmodel_dqmodelmethod; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_dqmodelmethod (
    id bigint NOT NULL,
    context_components jsonb NOT NULL,
    dq_model_id bigint NOT NULL,
    method_base_id bigint NOT NULL,
    metric_id bigint NOT NULL
);


ALTER TABLE public.dqmodel_dqmodelmethod OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 321891)
-- Name: dqmodel_dqmodelmethod_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dqmodel_dqmodelmethod_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dqmodel_dqmodelmethod_id_seq OWNER TO postgres;

--
-- TOC entry 3777 (class 0 OID 0)
-- Dependencies: 253
-- Name: dqmodel_dqmodelmethod_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dqmodel_dqmodelmethod_id_seq OWNED BY public.dqmodel_dqmodelmethod.id;


--
-- TOC entry 254 (class 1259 OID 321893)
-- Name: dqmodel_dqmodelmetric; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_dqmodelmetric (
    id bigint NOT NULL,
    context_components jsonb NOT NULL,
    dq_model_id bigint NOT NULL,
    factor_id bigint NOT NULL,
    metric_base_id bigint NOT NULL
);


ALTER TABLE public.dqmodel_dqmodelmetric OWNER TO postgres;

--
-- TOC entry 255 (class 1259 OID 321899)
-- Name: dqmodel_dqmodelmetric_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dqmodel_dqmodelmetric_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dqmodel_dqmodelmetric_id_seq OWNER TO postgres;

--
-- TOC entry 3778 (class 0 OID 0)
-- Dependencies: 255
-- Name: dqmodel_dqmodelmetric_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dqmodel_dqmodelmetric_id_seq OWNED BY public.dqmodel_dqmodelmetric.id;


--
-- TOC entry 256 (class 1259 OID 321901)
-- Name: dqmodel_measurementdqmethod; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dqmodel_measurementdqmethod (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    algorithm text NOT NULL,
    "appliedTo" jsonb NOT NULL,
    "associatedTo_id" bigint NOT NULL
);


ALTER TABLE public.dqmodel_measurementdqmethod OWNER TO postgres;

--
-- TOC entry 257 (class 1259 OID 321907)
-- Name: dqmodel_measurementdqmethod_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dqmodel_measurementdqmethod_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dqmodel_measurementdqmethod_id_seq OWNER TO postgres;

--
-- TOC entry 3779 (class 0 OID 0)
-- Dependencies: 257
-- Name: dqmodel_measurementdqmethod_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dqmodel_measurementdqmethod_id_seq OWNED BY public.dqmodel_measurementdqmethod.id;


--
-- TOC entry 258 (class 1259 OID 321909)
-- Name: estimation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estimation (
    id bigint NOT NULL,
    result jsonb NOT NULL,
    date date NOT NULL,
    manual_facts jsonb NOT NULL
);


ALTER TABLE public.estimation OWNER TO postgres;

--
-- TOC entry 259 (class 1259 OID 321915)
-- Name: estimation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.estimation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.estimation_id_seq OWNER TO postgres;

--
-- TOC entry 3780 (class 0 OID 0)
-- Dependencies: 259
-- Name: estimation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.estimation_id_seq OWNED BY public.estimation.id;


--
-- TOC entry 260 (class 1259 OID 321917)
-- Name: file_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.file_type (
    id bigint NOT NULL,
    type text
);


ALTER TABLE public.file_type OWNER TO postgres;

--
-- TOC entry 261 (class 1259 OID 321923)
-- Name: file_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.file_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.file_type_id_seq OWNER TO postgres;

--
-- TOC entry 3781 (class 0 OID 0)
-- Dependencies: 261
-- Name: file_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.file_type_id_seq OWNED BY public.file_type.id;


--
-- TOC entry 262 (class 1259 OID 321925)
-- Name: other_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.other_data (
    contextcomponent_ptr_id bigint NOT NULL,
    path character varying(255) NOT NULL,
    description text NOT NULL,
    owner character varying(255) NOT NULL
);


ALTER TABLE public.other_data OWNER TO postgres;

--
-- TOC entry 263 (class 1259 OID 321931)
-- Name: other_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.other_metadata (
    contextcomponent_ptr_id bigint NOT NULL,
    path character varying(255) NOT NULL,
    description text NOT NULL,
    author character varying(255) NOT NULL,
    last_update timestamp with time zone NOT NULL
);


ALTER TABLE public.other_metadata OWNER TO postgres;

--
-- TOC entry 264 (class 1259 OID 321937)
-- Name: project; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    created_at timestamp with time zone NOT NULL,
    data_at_hand_id bigint,
    user_id bigint NOT NULL,
    estimation_id bigint,
    context_id bigint,
    dqmodel_version_id bigint
);


ALTER TABLE public.project OWNER TO postgres;

--
-- TOC entry 265 (class 1259 OID 321943)
-- Name: project_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.project_id_seq OWNER TO postgres;

--
-- TOC entry 3782 (class 0 OID 0)
-- Dependencies: 265
-- Name: project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_id_seq OWNED BY public.project.id;


--
-- TOC entry 266 (class 1259 OID 321945)
-- Name: project_stage; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_stage (
    id bigint NOT NULL,
    stage character varying(50) NOT NULL,
    status character varying(50) NOT NULL,
    project_id bigint NOT NULL
);


ALTER TABLE public.project_stage OWNER TO postgres;

--
-- TOC entry 267 (class 1259 OID 321948)
-- Name: project_stage_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.project_stage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.project_stage_id_seq OWNER TO postgres;

--
-- TOC entry 3783 (class 0 OID 0)
-- Dependencies: 267
-- Name: project_stage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.project_stage_id_seq OWNED BY public.project_stage.id;


--
-- TOC entry 268 (class 1259 OID 321950)
-- Name: quality_problem; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quality_problem (
    id bigint NOT NULL,
    description text NOT NULL,
    date date NOT NULL,
    project_stage_id bigint
);


ALTER TABLE public.quality_problem OWNER TO postgres;

--
-- TOC entry 269 (class 1259 OID 321956)
-- Name: quality_problem_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quality_problem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quality_problem_id_seq OWNER TO postgres;

--
-- TOC entry 3784 (class 0 OID 0)
-- Dependencies: 269
-- Name: quality_problem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quality_problem_id_seq OWNED BY public.quality_problem.id;


--
-- TOC entry 270 (class 1259 OID 321958)
-- Name: quality_problem_project; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quality_problem_project (
    id bigint NOT NULL,
    priority character varying(10) NOT NULL,
    project_id bigint NOT NULL,
    quality_problem_id bigint NOT NULL,
    is_selected boolean NOT NULL
);


ALTER TABLE public.quality_problem_project OWNER TO postgres;

--
-- TOC entry 271 (class 1259 OID 321961)
-- Name: quality_problem_project_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quality_problem_project_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quality_problem_project_id_seq OWNER TO postgres;

--
-- TOC entry 3785 (class 0 OID 0)
-- Dependencies: 271
-- Name: quality_problem_project_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quality_problem_project_id_seq OWNED BY public.quality_problem_project.id;


--
-- TOC entry 272 (class 1259 OID 321963)
-- Name: quality_problem_reviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quality_problem_reviews (
    id integer NOT NULL,
    qualityproblem_id bigint NOT NULL,
    review_id bigint NOT NULL
);


ALTER TABLE public.quality_problem_reviews OWNER TO postgres;

--
-- TOC entry 273 (class 1259 OID 321966)
-- Name: quality_problem_reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quality_problem_reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quality_problem_reviews_id_seq OWNER TO postgres;

--
-- TOC entry 3786 (class 0 OID 0)
-- Dependencies: 273
-- Name: quality_problem_reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quality_problem_reviews_id_seq OWNED BY public.quality_problem_reviews.id;


--
-- TOC entry 274 (class 1259 OID 321968)
-- Name: review; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.review (
    id bigint NOT NULL,
    type character varying(50) NOT NULL,
    created_at date NOT NULL,
    data text,
    project_id bigint NOT NULL,
    user_id bigint,
    rejected_suggestions text
);


ALTER TABLE public.review OWNER TO postgres;

--
-- TOC entry 275 (class 1259 OID 321974)
-- Name: review_context_components; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.review_context_components (
    id integer NOT NULL,
    review_id bigint NOT NULL,
    contextcomponent_id bigint NOT NULL
);


ALTER TABLE public.review_context_components OWNER TO postgres;

--
-- TOC entry 276 (class 1259 OID 321977)
-- Name: review_context_components_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.review_context_components_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.review_context_components_id_seq OWNER TO postgres;

--
-- TOC entry 3787 (class 0 OID 0)
-- Dependencies: 276
-- Name: review_context_components_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.review_context_components_id_seq OWNED BY public.review_context_components.id;


--
-- TOC entry 277 (class 1259 OID 321979)
-- Name: review_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.review_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.review_id_seq OWNER TO postgres;

--
-- TOC entry 3788 (class 0 OID 0)
-- Dependencies: 277
-- Name: review_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.review_id_seq OWNED BY public.review.id;


--
-- TOC entry 278 (class 1259 OID 321981)
-- Name: review_quality_problems; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.review_quality_problems (
    id integer NOT NULL,
    review_id bigint NOT NULL,
    qualityproblem_id bigint NOT NULL
);


ALTER TABLE public.review_quality_problems OWNER TO postgres;

--
-- TOC entry 279 (class 1259 OID 321984)
-- Name: review_quality_problems_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.review_quality_problems_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.review_quality_problems_id_seq OWNER TO postgres;

--
-- TOC entry 3789 (class 0 OID 0)
-- Dependencies: 279
-- Name: review_quality_problems_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.review_quality_problems_id_seq OWNED BY public.review_quality_problems.id;


--
-- TOC entry 280 (class 1259 OID 321986)
-- Name: system_requirement; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_requirement (
    contextcomponent_ptr_id bigint NOT NULL,
    statement text NOT NULL,
    description text NOT NULL
);


ALTER TABLE public.system_requirement OWNER TO postgres;

--
-- TOC entry 281 (class 1259 OID 321992)
-- Name: task_at_hand; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_at_hand (
    contextcomponent_ptr_id bigint NOT NULL,
    name character varying(255) NOT NULL,
    purpose text NOT NULL
);


ALTER TABLE public.task_at_hand OWNER TO postgres;

--
-- TOC entry 282 (class 1259 OID 321998)
-- Name: task_at_hand_other_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_at_hand_other_data (
    id integer NOT NULL,
    taskathand_id bigint NOT NULL,
    otherdata_id bigint NOT NULL
);


ALTER TABLE public.task_at_hand_other_data OWNER TO postgres;

--
-- TOC entry 283 (class 1259 OID 322001)
-- Name: task_at_hand_other_data_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.task_at_hand_other_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_at_hand_other_data_id_seq OWNER TO postgres;

--
-- TOC entry 3790 (class 0 OID 0)
-- Dependencies: 283
-- Name: task_at_hand_other_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.task_at_hand_other_data_id_seq OWNED BY public.task_at_hand_other_data.id;


--
-- TOC entry 284 (class 1259 OID 322003)
-- Name: task_at_hand_system_requirements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_at_hand_system_requirements (
    id integer NOT NULL,
    taskathand_id bigint NOT NULL,
    systemrequirement_id bigint NOT NULL
);


ALTER TABLE public.task_at_hand_system_requirements OWNER TO postgres;

--
-- TOC entry 285 (class 1259 OID 322006)
-- Name: task_at_hand_system_requirements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.task_at_hand_system_requirements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_at_hand_system_requirements_id_seq OWNER TO postgres;

--
-- TOC entry 3791 (class 0 OID 0)
-- Dependencies: 285
-- Name: task_at_hand_system_requirements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.task_at_hand_system_requirements_id_seq OWNED BY public.task_at_hand_system_requirements.id;


--
-- TOC entry 286 (class 1259 OID 322008)
-- Name: task_at_hand_user_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_at_hand_user_types (
    id integer NOT NULL,
    taskathand_id bigint NOT NULL,
    usertype_id bigint NOT NULL
);


ALTER TABLE public.task_at_hand_user_types OWNER TO postgres;

--
-- TOC entry 287 (class 1259 OID 322011)
-- Name: task_at_hand_user_types_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.task_at_hand_user_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_at_hand_user_types_id_seq OWNER TO postgres;

--
-- TOC entry 3792 (class 0 OID 0)
-- Dependencies: 287
-- Name: task_at_hand_user_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.task_at_hand_user_types_id_seq OWNED BY public.task_at_hand_user_types.id;


--
-- TOC entry 288 (class 1259 OID 322013)
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id bigint NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    type character varying(50) NOT NULL,
    description text NOT NULL,
    username character varying(150)
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- TOC entry 289 (class 1259 OID 322019)
-- Name: user_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_data (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    description text NOT NULL,
    user_type_id bigint NOT NULL
);


ALTER TABLE public.user_data OWNER TO postgres;

--
-- TOC entry 290 (class 1259 OID 322025)
-- Name: user_data_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_data_id_seq OWNER TO postgres;

--
-- TOC entry 3793 (class 0 OID 0)
-- Dependencies: 290
-- Name: user_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_data_id_seq OWNED BY public.user_data.id;


--
-- TOC entry 291 (class 1259 OID 322027)
-- Name: user_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_groups (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.user_groups OWNER TO postgres;

--
-- TOC entry 292 (class 1259 OID 322030)
-- Name: user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_groups_id_seq OWNER TO postgres;

--
-- TOC entry 3794 (class 0 OID 0)
-- Dependencies: 292
-- Name: user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_groups_id_seq OWNED BY public.user_groups.id;


--
-- TOC entry 293 (class 1259 OID 322032)
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO postgres;

--
-- TOC entry 3795 (class 0 OID 0)
-- Dependencies: 293
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- TOC entry 294 (class 1259 OID 322034)
-- Name: user_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_type (
    contextcomponent_ptr_id bigint NOT NULL,
    name character varying(255) NOT NULL,
    characteristics text NOT NULL
);


ALTER TABLE public.user_type OWNER TO postgres;

--
-- TOC entry 295 (class 1259 OID 322040)
-- Name: user_user_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_user_permissions (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.user_user_permissions OWNER TO postgres;

--
-- TOC entry 296 (class 1259 OID 322043)
-- Name: user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_user_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_user_permissions_id_seq OWNER TO postgres;

--
-- TOC entry 3796 (class 0 OID 0)
-- Dependencies: 296
-- Name: user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_user_permissions_id_seq OWNED BY public.user_user_permissions.id;


--
-- TOC entry 3181 (class 2604 OID 322045)
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- TOC entry 3182 (class 2604 OID 322046)
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- TOC entry 3183 (class 2604 OID 322047)
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- TOC entry 3184 (class 2604 OID 322048)
-- Name: context id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context ALTER COLUMN id SET DEFAULT nextval('public.context_id_seq'::regclass);


--
-- TOC entry 3185 (class 2604 OID 322049)
-- Name: context_component id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context_component ALTER COLUMN id SET DEFAULT nextval('public.context_component_id_seq'::regclass);


--
-- TOC entry 3186 (class 2604 OID 322050)
-- Name: context_context_components id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context_context_components ALTER COLUMN id SET DEFAULT nextval('public.context_context_components_id_seq'::regclass);


--
-- TOC entry 3187 (class 2604 OID 322051)
-- Name: data_at_hand id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_at_hand ALTER COLUMN id SET DEFAULT nextval('public.data_at_hand_id_seq'::regclass);


--
-- TOC entry 3188 (class 2604 OID 322052)
-- Name: data_profiling id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_profiling ALTER COLUMN id SET DEFAULT nextval('public.data_profiling_id_seq'::regclass);


--
-- TOC entry 3189 (class 2604 OID 322053)
-- Name: data_profiling_context_components id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_profiling_context_components ALTER COLUMN id SET DEFAULT nextval('public.data_profiling_context_components_id_seq'::regclass);


--
-- TOC entry 3190 (class 2604 OID 322054)
-- Name: data_schema id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_schema ALTER COLUMN id SET DEFAULT nextval('public.data_schema_id_seq'::regclass);


--
-- TOC entry 3191 (class 2604 OID 322055)
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- TOC entry 3193 (class 2604 OID 322056)
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- TOC entry 3194 (class 2604 OID 322057)
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- TOC entry 3196 (class 2604 OID 322058)
-- Name: dq_requirement_data_filtering id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dq_requirement_data_filtering ALTER COLUMN id SET DEFAULT nextval('public.dq_requirement_data_filtering_id_seq'::regclass);


--
-- TOC entry 3197 (class 2604 OID 322059)
-- Name: dqmodel_aggregationdqmethod id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_aggregationdqmethod ALTER COLUMN id SET DEFAULT nextval('public.dqmodel_aggregationdqmethod_id_seq'::regclass);


--
-- TOC entry 3198 (class 2604 OID 322060)
-- Name: dqmodel_dqdimensionbase id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqdimensionbase ALTER COLUMN id SET DEFAULT nextval('public.dqmodel_dqdimensionbase_id_seq'::regclass);


--
-- TOC entry 3199 (class 2604 OID 322061)
-- Name: dqmodel_dqfactorbase id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqfactorbase ALTER COLUMN id SET DEFAULT nextval('public.dqmodel_dqfactorbase_id_seq'::regclass);


--
-- TOC entry 3200 (class 2604 OID 322062)
-- Name: dqmodel_dqmethodbase id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmethodbase ALTER COLUMN id SET DEFAULT nextval('public.dqmodel_dqmethodbase_id_seq'::regclass);


--
-- TOC entry 3201 (class 2604 OID 322063)
-- Name: dqmodel_dqmetricbase id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmetricbase ALTER COLUMN id SET DEFAULT nextval('public.dqmodel_dqmetricbase_id_seq'::regclass);


--
-- TOC entry 3195 (class 2604 OID 322064)
-- Name: dqmodel_dqmodel id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodel ALTER COLUMN id SET DEFAULT nextval('public.dq_model_id_seq'::regclass);


--
-- TOC entry 3202 (class 2604 OID 322065)
-- Name: dqmodel_dqmodeldimension id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodeldimension ALTER COLUMN id SET DEFAULT nextval('public.dqmodel_dqmodeldimension_id_seq'::regclass);


--
-- TOC entry 3203 (class 2604 OID 322066)
-- Name: dqmodel_dqmodelfactor id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelfactor ALTER COLUMN id SET DEFAULT nextval('public.dqmodel_dqmodelfactor_id_seq'::regclass);


--
-- TOC entry 3204 (class 2604 OID 322067)
-- Name: dqmodel_dqmodelmethod id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelmethod ALTER COLUMN id SET DEFAULT nextval('public.dqmodel_dqmodelmethod_id_seq'::regclass);


--
-- TOC entry 3205 (class 2604 OID 322068)
-- Name: dqmodel_dqmodelmetric id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelmetric ALTER COLUMN id SET DEFAULT nextval('public.dqmodel_dqmodelmetric_id_seq'::regclass);


--
-- TOC entry 3206 (class 2604 OID 322069)
-- Name: dqmodel_measurementdqmethod id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_measurementdqmethod ALTER COLUMN id SET DEFAULT nextval('public.dqmodel_measurementdqmethod_id_seq'::regclass);


--
-- TOC entry 3207 (class 2604 OID 322070)
-- Name: estimation id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estimation ALTER COLUMN id SET DEFAULT nextval('public.estimation_id_seq'::regclass);


--
-- TOC entry 3208 (class 2604 OID 322071)
-- Name: file_type id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_type ALTER COLUMN id SET DEFAULT nextval('public.file_type_id_seq'::regclass);


--
-- TOC entry 3209 (class 2604 OID 322072)
-- Name: project id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project ALTER COLUMN id SET DEFAULT nextval('public.project_id_seq'::regclass);


--
-- TOC entry 3210 (class 2604 OID 322073)
-- Name: project_stage id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_stage ALTER COLUMN id SET DEFAULT nextval('public.project_stage_id_seq'::regclass);


--
-- TOC entry 3211 (class 2604 OID 322074)
-- Name: quality_problem id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem ALTER COLUMN id SET DEFAULT nextval('public.quality_problem_id_seq'::regclass);


--
-- TOC entry 3212 (class 2604 OID 322075)
-- Name: quality_problem_project id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem_project ALTER COLUMN id SET DEFAULT nextval('public.quality_problem_project_id_seq'::regclass);


--
-- TOC entry 3213 (class 2604 OID 322076)
-- Name: quality_problem_reviews id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem_reviews ALTER COLUMN id SET DEFAULT nextval('public.quality_problem_reviews_id_seq'::regclass);


--
-- TOC entry 3214 (class 2604 OID 322077)
-- Name: review id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review ALTER COLUMN id SET DEFAULT nextval('public.review_id_seq'::regclass);


--
-- TOC entry 3215 (class 2604 OID 322078)
-- Name: review_context_components id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_context_components ALTER COLUMN id SET DEFAULT nextval('public.review_context_components_id_seq'::regclass);


--
-- TOC entry 3216 (class 2604 OID 322079)
-- Name: review_quality_problems id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_quality_problems ALTER COLUMN id SET DEFAULT nextval('public.review_quality_problems_id_seq'::regclass);


--
-- TOC entry 3217 (class 2604 OID 322080)
-- Name: task_at_hand_other_data id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_other_data ALTER COLUMN id SET DEFAULT nextval('public.task_at_hand_other_data_id_seq'::regclass);


--
-- TOC entry 3218 (class 2604 OID 322081)
-- Name: task_at_hand_system_requirements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_system_requirements ALTER COLUMN id SET DEFAULT nextval('public.task_at_hand_system_requirements_id_seq'::regclass);


--
-- TOC entry 3219 (class 2604 OID 322082)
-- Name: task_at_hand_user_types id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_user_types ALTER COLUMN id SET DEFAULT nextval('public.task_at_hand_user_types_id_seq'::regclass);


--
-- TOC entry 3180 (class 2604 OID 322083)
-- Name: uploaded_file id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploaded_file ALTER COLUMN id SET DEFAULT nextval('public."CaDQM_backend_uploadedfile_id_seq"'::regclass);


--
-- TOC entry 3220 (class 2604 OID 322084)
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- TOC entry 3221 (class 2604 OID 322085)
-- Name: user_data id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_data ALTER COLUMN id SET DEFAULT nextval('public.user_data_id_seq'::regclass);


--
-- TOC entry 3222 (class 2604 OID 322086)
-- Name: user_groups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_groups ALTER COLUMN id SET DEFAULT nextval('public.user_groups_id_seq'::regclass);


--
-- TOC entry 3223 (class 2604 OID 322087)
-- Name: user_user_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.user_user_permissions_id_seq'::regclass);


--
-- TOC entry 3654 (class 0 OID 321702)
-- Dependencies: 202
-- Data for Name: application_domain; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.application_domain (contextcomponent_ptr_id, description) FROM stdin;
\.


--
-- TOC entry 3655 (class 0 OID 321708)
-- Dependencies: 203
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- TOC entry 3657 (class 0 OID 321713)
-- Dependencies: 205
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- TOC entry 3659 (class 0 OID 321718)
-- Dependencies: 207
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
\.


--
-- TOC entry 3661 (class 0 OID 321723)
-- Dependencies: 209
-- Data for Name: business_rule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.business_rule (contextcomponent_ptr_id, statement, semantic) FROM stdin;
\.


--
-- TOC entry 3662 (class 0 OID 321729)
-- Dependencies: 210
-- Data for Name: context; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.context (id, name, version, previous_version_id) FROM stdin;
1	Context Test 01	1.0.0	\N
\.


--
-- TOC entry 3663 (class 0 OID 321732)
-- Dependencies: 211
-- Data for Name: context_component; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.context_component (id, project_stage_id) FROM stdin;
\.


--
-- TOC entry 3665 (class 0 OID 321737)
-- Dependencies: 213
-- Data for Name: context_context_components; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.context_context_components (id, context_id, contextcomponent_id) FROM stdin;
\.


--
-- TOC entry 3668 (class 0 OID 321744)
-- Dependencies: 216
-- Data for Name: data_at_hand; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_at_hand (id, name, description, date, url_db, user_db, pass_db, port, type) FROM stdin;
\.


--
-- TOC entry 3670 (class 0 OID 321752)
-- Dependencies: 218
-- Data for Name: data_filtering; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_filtering (contextcomponent_ptr_id, statement, description, task_at_hand_id) FROM stdin;
\.


--
-- TOC entry 3671 (class 0 OID 321758)
-- Dependencies: 219
-- Data for Name: data_profiling; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_profiling (id, description, type, result, date, project_id) FROM stdin;
\.


--
-- TOC entry 3672 (class 0 OID 321764)
-- Dependencies: 220
-- Data for Name: data_profiling_context_components; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_profiling_context_components (id, dataprofiling_id, contextcomponent_id) FROM stdin;
\.


--
-- TOC entry 3675 (class 0 OID 321771)
-- Dependencies: 223
-- Data for Name: data_schema; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.data_schema (id, data_at_hand_id, schema) FROM stdin;
\.


--
-- TOC entry 3677 (class 0 OID 321779)
-- Dependencies: 225
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2025-09-06 17:47:16.501583-03	2	Project Test 01	2	[{"changed": {"fields": ["Context"]}}]	1	1
2	2025-09-06 21:20:16.954128-03	3	Consistency	2	[{"changed": {"fields": ["Semantic"]}}]	2	1
\.


--
-- TOC entry 3679 (class 0 OID 321788)
-- Dependencies: 227
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	project	project
2	dqmodel	dqdimensionbase
\.


--
-- TOC entry 3681 (class 0 OID 321793)
-- Dependencies: 229
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
\.


--
-- TOC entry 3683 (class 0 OID 321801)
-- Dependencies: 231
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
f5d8cdsjaas2kpoe2mezngp4mbp8grba	.eJxVjEEOgjAQRe_StWkYWqYdl-49QzPTKYIaSCisjHdXEha6_e-9_zKJt3VIWy1LGtWcDZjT7yacH2Xagd55us02z9O6jGJ3xR602uus5Xk53L-DgevwrZvOEzEU6tT7LBwAQgPZicYW-xBj77wQU3GAnhFjS6KIik4kE4h5fwDKizeA:1uuzoG:vgmLlCgc9tO2vffnJDUOmcBlTZVcchIRkNseRajNdP4	2025-09-20 17:46:56.703325-03
\.


--
-- TOC entry 3684 (class 0 OID 321807)
-- Dependencies: 232
-- Data for Name: dq_metadata; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dq_metadata (contextcomponent_ptr_id, path, description, measurement) FROM stdin;
\.


--
-- TOC entry 3687 (class 0 OID 321818)
-- Dependencies: 235
-- Data for Name: dq_requirement; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dq_requirement (contextcomponent_ptr_id, statement, description, user_type_id) FROM stdin;
\.


--
-- TOC entry 3688 (class 0 OID 321824)
-- Dependencies: 236
-- Data for Name: dq_requirement_data_filtering; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dq_requirement_data_filtering (id, dqrequirement_id, datafiltering_id) FROM stdin;
\.


--
-- TOC entry 3690 (class 0 OID 321829)
-- Dependencies: 238
-- Data for Name: dqmodel_aggregationdqmethod; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_aggregationdqmethod (id, name, algorithm, "appliedTo", "associatedTo_id") FROM stdin;
\.


--
-- TOC entry 3692 (class 0 OID 321837)
-- Dependencies: 240
-- Data for Name: dqmodel_dqdimensionbase; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_dqdimensionbase (id, name, semantic, is_disabled) FROM stdin;
1	Accuracy	Indicates the degree to which data is accurate. Refers to how well data correctly represents real-world objects or events.	f
2	Completeness	Refers to the availability of all necessary data, ensuring that no important data is missing for analysis or decision-making.	f
4	Uniqueness	Indicates the degree to which a real-world entity is represented only once in the information system, without duplication or contradiction.	f
5	Freshness	Refers to the temporal validity of the data, indicating how current, timely, or stable the data is with respect to its use and the real world.	f
3	Consistency	Indicates the satisfaction of semantic rules defined on the data.	f
\.


--
-- TOC entry 3694 (class 0 OID 321845)
-- Dependencies: 242
-- Data for Name: dqmodel_dqfactorbase; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_dqfactorbase (id, name, semantic, is_disabled, "facetOf_id") FROM stdin;
1	Semantic Accuracy	Indicates the degree to which data correctly represents real-world entities or states.	f	1
2	Syntactic Accuracy	Indicates the degree to which data conforms to expected structural formats, patterns, or data types.	f	1
3	Precision	Refers to the level of detail in which data is captured or expressed.	f	1
4	Density	Describes the proportion of actual data entries compared to the total number of expected entries.	f	2
5	Coverage	Indicates the extent to which the data covers the required scope, domain, or entities.	f	2
6	Domain Integrity	Indicates whether individual attribute values comply with defined constraints, rules, or value domains.	f	3
7	Intra-relationship Integrity	Indicates whether values across multiple attributes within the same record or table satisfy logical rules or dependencies.	f	3
8	Inter-relationship Integrity	Indicates whether data relationships across different tables or entities satisfy expected referential and semantic rules.	f	3
9	No-duplication	Indicates the absence of duplicate records within the dataset.	f	4
10	No-contradiction	Ensures that logically related records do not contain conflicting or contradictory information.	f	4
11	Currency	Indicates how up-to-date the data is with respect to the real-world entities or source systems it represents.	f	5
12	Timeliness	Indicates whether data is available in time to support its intended use.	f	5
13	Volatility	Describes the frequency or rate at which the data changes over time.	f	5
\.


--
-- TOC entry 3696 (class 0 OID 321853)
-- Dependencies: 244
-- Data for Name: dqmodel_dqmethodbase; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_dqmethodbase (id, name, "inputDataType", "outputDataType", algorithm, is_disabled, implements_id) FROM stdin;
\.


--
-- TOC entry 3698 (class 0 OID 321861)
-- Dependencies: 246
-- Data for Name: dqmodel_dqmetricbase; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_dqmetricbase (id, name, purpose, granularity, "resultDomain", is_disabled, measures_id) FROM stdin;
\.


--
-- TOC entry 3685 (class 0 OID 321813)
-- Dependencies: 233
-- Data for Name: dqmodel_dqmodel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_dqmodel (id, name, version, created_at, previous_version_id, finished_at, status) FROM stdin;
\.


--
-- TOC entry 3700 (class 0 OID 321869)
-- Dependencies: 248
-- Data for Name: dqmodel_dqmodeldimension; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_dqmodeldimension (id, context_components, dq_problems, dimension_base_id, dq_model_id) FROM stdin;
\.


--
-- TOC entry 3702 (class 0 OID 321877)
-- Dependencies: 250
-- Data for Name: dqmodel_dqmodelfactor; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_dqmodelfactor (id, context_components, dq_problems, dimension_id, dq_model_id, factor_base_id) FROM stdin;
\.


--
-- TOC entry 3704 (class 0 OID 321885)
-- Dependencies: 252
-- Data for Name: dqmodel_dqmodelmethod; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_dqmodelmethod (id, context_components, dq_model_id, method_base_id, metric_id) FROM stdin;
\.


--
-- TOC entry 3706 (class 0 OID 321893)
-- Dependencies: 254
-- Data for Name: dqmodel_dqmodelmetric; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_dqmodelmetric (id, context_components, dq_model_id, factor_id, metric_base_id) FROM stdin;
\.


--
-- TOC entry 3708 (class 0 OID 321901)
-- Dependencies: 256
-- Data for Name: dqmodel_measurementdqmethod; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dqmodel_measurementdqmethod (id, name, algorithm, "appliedTo", "associatedTo_id") FROM stdin;
\.


--
-- TOC entry 3710 (class 0 OID 321909)
-- Dependencies: 258
-- Data for Name: estimation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.estimation (id, result, date, manual_facts) FROM stdin;
\.


--
-- TOC entry 3712 (class 0 OID 321917)
-- Dependencies: 260
-- Data for Name: file_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.file_type (id, type) FROM stdin;
\.


--
-- TOC entry 3714 (class 0 OID 321925)
-- Dependencies: 262
-- Data for Name: other_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.other_data (contextcomponent_ptr_id, path, description, owner) FROM stdin;
\.


--
-- TOC entry 3715 (class 0 OID 321931)
-- Dependencies: 263
-- Data for Name: other_metadata; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.other_metadata (contextcomponent_ptr_id, path, description, author, last_update) FROM stdin;
\.


--
-- TOC entry 3716 (class 0 OID 321937)
-- Dependencies: 264
-- Data for Name: project; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project (id, name, description, created_at, data_at_hand_id, user_id, estimation_id, context_id, dqmodel_version_id) FROM stdin;
2	Project Test 01	Empty Project Test 01	2025-09-06 17:44:49.516768-03	\N	1	\N	1	\N
\.


--
-- TOC entry 3718 (class 0 OID 321945)
-- Dependencies: 266
-- Data for Name: project_stage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_stage (id, stage, status, project_id) FROM stdin;
1	ST1	DONE	2
2	ST2	DONE	2
3	ST3	DONE	2
4	ST4	TO_DO	2
5	ST5	TO_DO	2
6	ST6	TO_DO	2
\.


--
-- TOC entry 3720 (class 0 OID 321950)
-- Dependencies: 268
-- Data for Name: quality_problem; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quality_problem (id, description, date, project_stage_id) FROM stdin;
\.


--
-- TOC entry 3722 (class 0 OID 321958)
-- Dependencies: 270
-- Data for Name: quality_problem_project; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quality_problem_project (id, priority, project_id, quality_problem_id, is_selected) FROM stdin;
\.


--
-- TOC entry 3724 (class 0 OID 321963)
-- Dependencies: 272
-- Data for Name: quality_problem_reviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.quality_problem_reviews (id, qualityproblem_id, review_id) FROM stdin;
\.


--
-- TOC entry 3726 (class 0 OID 321968)
-- Dependencies: 274
-- Data for Name: review; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.review (id, type, created_at, data, project_id, user_id, rejected_suggestions) FROM stdin;
\.


--
-- TOC entry 3727 (class 0 OID 321974)
-- Dependencies: 275
-- Data for Name: review_context_components; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.review_context_components (id, review_id, contextcomponent_id) FROM stdin;
\.


--
-- TOC entry 3730 (class 0 OID 321981)
-- Dependencies: 278
-- Data for Name: review_quality_problems; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.review_quality_problems (id, review_id, qualityproblem_id) FROM stdin;
\.


--
-- TOC entry 3732 (class 0 OID 321986)
-- Dependencies: 280
-- Data for Name: system_requirement; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_requirement (contextcomponent_ptr_id, statement, description) FROM stdin;
\.


--
-- TOC entry 3733 (class 0 OID 321992)
-- Dependencies: 281
-- Data for Name: task_at_hand; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_at_hand (contextcomponent_ptr_id, name, purpose) FROM stdin;
\.


--
-- TOC entry 3734 (class 0 OID 321998)
-- Dependencies: 282
-- Data for Name: task_at_hand_other_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_at_hand_other_data (id, taskathand_id, otherdata_id) FROM stdin;
\.


--
-- TOC entry 3736 (class 0 OID 322003)
-- Dependencies: 284
-- Data for Name: task_at_hand_system_requirements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_at_hand_system_requirements (id, taskathand_id, systemrequirement_id) FROM stdin;
\.


--
-- TOC entry 3738 (class 0 OID 322008)
-- Dependencies: 286
-- Data for Name: task_at_hand_user_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.task_at_hand_user_types (id, taskathand_id, usertype_id) FROM stdin;
\.


--
-- TOC entry 3652 (class 0 OID 321694)
-- Dependencies: 200
-- Data for Name: uploaded_file; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.uploaded_file (id, file, uploaded_at, analysis, review_id, description, file_type_id) FROM stdin;
\.


--
-- TOC entry 3740 (class 0 OID 322013)
-- Dependencies: 288
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."user" (id, password, last_login, is_superuser, first_name, last_name, email, is_staff, is_active, date_joined, type, description, username) FROM stdin;
1	pbkdf2_sha256$720000$PRpNe11MsNP9xMhFSGJ7Kq$ruEkyFMCKcTe7g7UOxANWxnv0jZ1ouidSPGBtAbXuHI=	2025-09-06 17:46:56.699326-03	t				t	t	2025-09-06 17:44:34.614568-03			admin
\.


--
-- TOC entry 3741 (class 0 OID 322019)
-- Dependencies: 289
-- Data for Name: user_data; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_data (id, name, description, user_type_id) FROM stdin;
\.


--
-- TOC entry 3743 (class 0 OID 322027)
-- Dependencies: 291
-- Data for Name: user_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- TOC entry 3746 (class 0 OID 322034)
-- Dependencies: 294
-- Data for Name: user_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_type (contextcomponent_ptr_id, name, characteristics) FROM stdin;
\.


--
-- TOC entry 3747 (class 0 OID 322040)
-- Dependencies: 295
-- Data for Name: user_user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- TOC entry 3797 (class 0 OID 0)
-- Dependencies: 201
-- Name: CaDQM_backend_uploadedfile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."CaDQM_backend_uploadedfile_id_seq"', 1, false);


--
-- TOC entry 3798 (class 0 OID 0)
-- Dependencies: 204
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- TOC entry 3799 (class 0 OID 0)
-- Dependencies: 206
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- TOC entry 3800 (class 0 OID 0)
-- Dependencies: 208
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 1, false);


--
-- TOC entry 3801 (class 0 OID 0)
-- Dependencies: 212
-- Name: context_component_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.context_component_id_seq', 1, false);


--
-- TOC entry 3802 (class 0 OID 0)
-- Dependencies: 214
-- Name: context_context_components_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.context_context_components_id_seq', 1, false);


--
-- TOC entry 3803 (class 0 OID 0)
-- Dependencies: 215
-- Name: context_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.context_id_seq', 1, true);


--
-- TOC entry 3804 (class 0 OID 0)
-- Dependencies: 217
-- Name: data_at_hand_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.data_at_hand_id_seq', 1, false);


--
-- TOC entry 3805 (class 0 OID 0)
-- Dependencies: 221
-- Name: data_profiling_context_components_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.data_profiling_context_components_id_seq', 1, false);


--
-- TOC entry 3806 (class 0 OID 0)
-- Dependencies: 222
-- Name: data_profiling_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.data_profiling_id_seq', 1, false);


--
-- TOC entry 3807 (class 0 OID 0)
-- Dependencies: 224
-- Name: data_schema_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.data_schema_id_seq', 1, false);


--
-- TOC entry 3808 (class 0 OID 0)
-- Dependencies: 226
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 2, true);


--
-- TOC entry 3809 (class 0 OID 0)
-- Dependencies: 228
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 2, true);


--
-- TOC entry 3810 (class 0 OID 0)
-- Dependencies: 230
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 1, false);


--
-- TOC entry 3811 (class 0 OID 0)
-- Dependencies: 234
-- Name: dq_model_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dq_model_id_seq', 1, false);


--
-- TOC entry 3812 (class 0 OID 0)
-- Dependencies: 237
-- Name: dq_requirement_data_filtering_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dq_requirement_data_filtering_id_seq', 1, false);


--
-- TOC entry 3813 (class 0 OID 0)
-- Dependencies: 239
-- Name: dqmodel_aggregationdqmethod_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dqmodel_aggregationdqmethod_id_seq', 1, false);


--
-- TOC entry 3814 (class 0 OID 0)
-- Dependencies: 241
-- Name: dqmodel_dqdimensionbase_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dqmodel_dqdimensionbase_id_seq', 5, true);


--
-- TOC entry 3815 (class 0 OID 0)
-- Dependencies: 243
-- Name: dqmodel_dqfactorbase_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dqmodel_dqfactorbase_id_seq', 13, true);


--
-- TOC entry 3816 (class 0 OID 0)
-- Dependencies: 245
-- Name: dqmodel_dqmethodbase_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dqmodel_dqmethodbase_id_seq', 1, false);


--
-- TOC entry 3817 (class 0 OID 0)
-- Dependencies: 247
-- Name: dqmodel_dqmetricbase_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dqmodel_dqmetricbase_id_seq', 1, false);


--
-- TOC entry 3818 (class 0 OID 0)
-- Dependencies: 249
-- Name: dqmodel_dqmodeldimension_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dqmodel_dqmodeldimension_id_seq', 1, false);


--
-- TOC entry 3819 (class 0 OID 0)
-- Dependencies: 251
-- Name: dqmodel_dqmodelfactor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dqmodel_dqmodelfactor_id_seq', 1, false);


--
-- TOC entry 3820 (class 0 OID 0)
-- Dependencies: 253
-- Name: dqmodel_dqmodelmethod_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dqmodel_dqmodelmethod_id_seq', 1, false);


--
-- TOC entry 3821 (class 0 OID 0)
-- Dependencies: 255
-- Name: dqmodel_dqmodelmetric_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dqmodel_dqmodelmetric_id_seq', 1, false);


--
-- TOC entry 3822 (class 0 OID 0)
-- Dependencies: 257
-- Name: dqmodel_measurementdqmethod_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dqmodel_measurementdqmethod_id_seq', 1, false);


--
-- TOC entry 3823 (class 0 OID 0)
-- Dependencies: 259
-- Name: estimation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.estimation_id_seq', 1, false);


--
-- TOC entry 3824 (class 0 OID 0)
-- Dependencies: 261
-- Name: file_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.file_type_id_seq', 1, false);


--
-- TOC entry 3825 (class 0 OID 0)
-- Dependencies: 265
-- Name: project_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_id_seq', 2, true);


--
-- TOC entry 3826 (class 0 OID 0)
-- Dependencies: 267
-- Name: project_stage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.project_stage_id_seq', 6, true);


--
-- TOC entry 3827 (class 0 OID 0)
-- Dependencies: 269
-- Name: quality_problem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quality_problem_id_seq', 1, false);


--
-- TOC entry 3828 (class 0 OID 0)
-- Dependencies: 271
-- Name: quality_problem_project_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quality_problem_project_id_seq', 1, false);


--
-- TOC entry 3829 (class 0 OID 0)
-- Dependencies: 273
-- Name: quality_problem_reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.quality_problem_reviews_id_seq', 1, false);


--
-- TOC entry 3830 (class 0 OID 0)
-- Dependencies: 276
-- Name: review_context_components_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.review_context_components_id_seq', 1, false);


--
-- TOC entry 3831 (class 0 OID 0)
-- Dependencies: 277
-- Name: review_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.review_id_seq', 1, false);


--
-- TOC entry 3832 (class 0 OID 0)
-- Dependencies: 279
-- Name: review_quality_problems_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.review_quality_problems_id_seq', 1, false);


--
-- TOC entry 3833 (class 0 OID 0)
-- Dependencies: 283
-- Name: task_at_hand_other_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.task_at_hand_other_data_id_seq', 1, false);


--
-- TOC entry 3834 (class 0 OID 0)
-- Dependencies: 285
-- Name: task_at_hand_system_requirements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.task_at_hand_system_requirements_id_seq', 1, false);


--
-- TOC entry 3835 (class 0 OID 0)
-- Dependencies: 287
-- Name: task_at_hand_user_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.task_at_hand_user_types_id_seq', 1, false);


--
-- TOC entry 3836 (class 0 OID 0)
-- Dependencies: 290
-- Name: user_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_data_id_seq', 1, false);


--
-- TOC entry 3837 (class 0 OID 0)
-- Dependencies: 292
-- Name: user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_groups_id_seq', 1, false);


--
-- TOC entry 3838 (class 0 OID 0)
-- Dependencies: 293
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_id_seq', 1, true);


--
-- TOC entry 3839 (class 0 OID 0)
-- Dependencies: 296
-- Name: user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_user_permissions_id_seq', 1, false);


--
-- TOC entry 3225 (class 2606 OID 322091)
-- Name: uploaded_file CaDQM_backend_uploadedfile_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploaded_file
    ADD CONSTRAINT "CaDQM_backend_uploadedfile_pkey" PRIMARY KEY (id);


--
-- TOC entry 3229 (class 2606 OID 322093)
-- Name: application_domain application_domain_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.application_domain
    ADD CONSTRAINT application_domain_pkey PRIMARY KEY (contextcomponent_ptr_id);


--
-- TOC entry 3232 (class 2606 OID 322095)
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- TOC entry 3237 (class 2606 OID 322097)
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- TOC entry 3240 (class 2606 OID 322099)
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 3234 (class 2606 OID 322101)
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- TOC entry 3243 (class 2606 OID 322103)
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- TOC entry 3245 (class 2606 OID 322105)
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- TOC entry 3247 (class 2606 OID 322107)
-- Name: business_rule business_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_rule
    ADD CONSTRAINT business_rule_pkey PRIMARY KEY (contextcomponent_ptr_id);


--
-- TOC entry 3252 (class 2606 OID 322109)
-- Name: context_component context_component_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context_component
    ADD CONSTRAINT context_component_pkey PRIMARY KEY (id);


--
-- TOC entry 3255 (class 2606 OID 322111)
-- Name: context_context_components context_context_componen_context_id_contextcompon_0579da66_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context_context_components
    ADD CONSTRAINT context_context_componen_context_id_contextcompon_0579da66_uniq UNIQUE (context_id, contextcomponent_id);


--
-- TOC entry 3259 (class 2606 OID 322113)
-- Name: context_context_components context_context_components_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context_context_components
    ADD CONSTRAINT context_context_components_pkey PRIMARY KEY (id);


--
-- TOC entry 3249 (class 2606 OID 322115)
-- Name: context context_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context
    ADD CONSTRAINT context_pkey PRIMARY KEY (id);


--
-- TOC entry 3261 (class 2606 OID 322117)
-- Name: data_at_hand data_at_hand_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_at_hand
    ADD CONSTRAINT data_at_hand_pkey PRIMARY KEY (id);


--
-- TOC entry 3263 (class 2606 OID 322119)
-- Name: data_filtering data_filtering_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_filtering
    ADD CONSTRAINT data_filtering_pkey PRIMARY KEY (contextcomponent_ptr_id);


--
-- TOC entry 3269 (class 2606 OID 322121)
-- Name: data_profiling_context_components data_profiling_context_c_dataprofiling_id_context_2f661741_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_profiling_context_components
    ADD CONSTRAINT data_profiling_context_c_dataprofiling_id_context_2f661741_uniq UNIQUE (dataprofiling_id, contextcomponent_id);


--
-- TOC entry 3273 (class 2606 OID 322123)
-- Name: data_profiling_context_components data_profiling_context_components_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_profiling_context_components
    ADD CONSTRAINT data_profiling_context_components_pkey PRIMARY KEY (id);


--
-- TOC entry 3266 (class 2606 OID 322125)
-- Name: data_profiling data_profiling_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_profiling
    ADD CONSTRAINT data_profiling_pkey PRIMARY KEY (id);


--
-- TOC entry 3275 (class 2606 OID 322127)
-- Name: data_schema data_schema_data_at_hand_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_schema
    ADD CONSTRAINT data_schema_data_at_hand_id_key UNIQUE (data_at_hand_id);


--
-- TOC entry 3277 (class 2606 OID 322129)
-- Name: data_schema data_schema_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_schema
    ADD CONSTRAINT data_schema_pkey PRIMARY KEY (id);


--
-- TOC entry 3280 (class 2606 OID 322131)
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- TOC entry 3283 (class 2606 OID 322133)
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- TOC entry 3285 (class 2606 OID 322135)
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- TOC entry 3287 (class 2606 OID 322137)
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- TOC entry 3290 (class 2606 OID 322139)
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- TOC entry 3293 (class 2606 OID 322141)
-- Name: dq_metadata dq_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dq_metadata
    ADD CONSTRAINT dq_metadata_pkey PRIMARY KEY (contextcomponent_ptr_id);


--
-- TOC entry 3295 (class 2606 OID 322143)
-- Name: dqmodel_dqmodel dq_model_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodel
    ADD CONSTRAINT dq_model_pkey PRIMARY KEY (id);


--
-- TOC entry 3301 (class 2606 OID 322145)
-- Name: dq_requirement_data_filtering dq_requirement_data_filt_dqrequirement_id_datafil_e282dfb7_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dq_requirement_data_filtering
    ADD CONSTRAINT dq_requirement_data_filt_dqrequirement_id_datafil_e282dfb7_uniq UNIQUE (dqrequirement_id, datafiltering_id);


--
-- TOC entry 3305 (class 2606 OID 322147)
-- Name: dq_requirement_data_filtering dq_requirement_data_filtering_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dq_requirement_data_filtering
    ADD CONSTRAINT dq_requirement_data_filtering_pkey PRIMARY KEY (id);


--
-- TOC entry 3298 (class 2606 OID 322149)
-- Name: dq_requirement dq_requirement_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dq_requirement
    ADD CONSTRAINT dq_requirement_pkey PRIMARY KEY (contextcomponent_ptr_id);


--
-- TOC entry 3308 (class 2606 OID 322151)
-- Name: dqmodel_aggregationdqmethod dqmodel_aggregationdqmethod_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_aggregationdqmethod
    ADD CONSTRAINT dqmodel_aggregationdqmethod_pkey PRIMARY KEY (id);


--
-- TOC entry 3311 (class 2606 OID 322153)
-- Name: dqmodel_dqdimensionbase dqmodel_dqdimensionbase_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqdimensionbase
    ADD CONSTRAINT dqmodel_dqdimensionbase_name_key UNIQUE (name);


--
-- TOC entry 3313 (class 2606 OID 322155)
-- Name: dqmodel_dqdimensionbase dqmodel_dqdimensionbase_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqdimensionbase
    ADD CONSTRAINT dqmodel_dqdimensionbase_pkey PRIMARY KEY (id);


--
-- TOC entry 3317 (class 2606 OID 322157)
-- Name: dqmodel_dqfactorbase dqmodel_dqfactorbase_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqfactorbase
    ADD CONSTRAINT dqmodel_dqfactorbase_name_key UNIQUE (name);


--
-- TOC entry 3319 (class 2606 OID 322159)
-- Name: dqmodel_dqfactorbase dqmodel_dqfactorbase_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqfactorbase
    ADD CONSTRAINT dqmodel_dqfactorbase_pkey PRIMARY KEY (id);


--
-- TOC entry 3323 (class 2606 OID 322161)
-- Name: dqmodel_dqmethodbase dqmodel_dqmethodbase_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmethodbase
    ADD CONSTRAINT dqmodel_dqmethodbase_name_key UNIQUE (name);


--
-- TOC entry 3325 (class 2606 OID 322163)
-- Name: dqmodel_dqmethodbase dqmodel_dqmethodbase_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmethodbase
    ADD CONSTRAINT dqmodel_dqmethodbase_pkey PRIMARY KEY (id);


--
-- TOC entry 3329 (class 2606 OID 322165)
-- Name: dqmodel_dqmetricbase dqmodel_dqmetricbase_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmetricbase
    ADD CONSTRAINT dqmodel_dqmetricbase_name_key UNIQUE (name);


--
-- TOC entry 3331 (class 2606 OID 322167)
-- Name: dqmodel_dqmetricbase dqmodel_dqmetricbase_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmetricbase
    ADD CONSTRAINT dqmodel_dqmetricbase_pkey PRIMARY KEY (id);


--
-- TOC entry 3335 (class 2606 OID 322169)
-- Name: dqmodel_dqmodeldimension dqmodel_dqmodeldimension_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodeldimension
    ADD CONSTRAINT dqmodel_dqmodeldimension_pkey PRIMARY KEY (id);


--
-- TOC entry 3340 (class 2606 OID 322171)
-- Name: dqmodel_dqmodelfactor dqmodel_dqmodelfactor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelfactor
    ADD CONSTRAINT dqmodel_dqmodelfactor_pkey PRIMARY KEY (id);


--
-- TOC entry 3345 (class 2606 OID 322173)
-- Name: dqmodel_dqmodelmethod dqmodel_dqmodelmethod_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelmethod
    ADD CONSTRAINT dqmodel_dqmodelmethod_pkey PRIMARY KEY (id);


--
-- TOC entry 3350 (class 2606 OID 322175)
-- Name: dqmodel_dqmodelmetric dqmodel_dqmodelmetric_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelmetric
    ADD CONSTRAINT dqmodel_dqmodelmetric_pkey PRIMARY KEY (id);


--
-- TOC entry 3353 (class 2606 OID 322177)
-- Name: dqmodel_measurementdqmethod dqmodel_measurementdqmethod_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_measurementdqmethod
    ADD CONSTRAINT dqmodel_measurementdqmethod_pkey PRIMARY KEY (id);


--
-- TOC entry 3355 (class 2606 OID 322179)
-- Name: estimation estimation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estimation
    ADD CONSTRAINT estimation_pkey PRIMARY KEY (id);


--
-- TOC entry 3357 (class 2606 OID 322181)
-- Name: file_type file_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_type
    ADD CONSTRAINT file_type_pkey PRIMARY KEY (id);


--
-- TOC entry 3359 (class 2606 OID 322183)
-- Name: other_data other_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.other_data
    ADD CONSTRAINT other_data_pkey PRIMARY KEY (contextcomponent_ptr_id);


--
-- TOC entry 3361 (class 2606 OID 322185)
-- Name: other_metadata other_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.other_metadata
    ADD CONSTRAINT other_metadata_pkey PRIMARY KEY (contextcomponent_ptr_id);


--
-- TOC entry 3366 (class 2606 OID 322187)
-- Name: project project_estimation_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_estimation_id_key UNIQUE (estimation_id);


--
-- TOC entry 3368 (class 2606 OID 322189)
-- Name: project project_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_pkey PRIMARY KEY (id);


--
-- TOC entry 3371 (class 2606 OID 322191)
-- Name: project_stage project_stage_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_stage
    ADD CONSTRAINT project_stage_pkey PRIMARY KEY (id);


--
-- TOC entry 3374 (class 2606 OID 322193)
-- Name: quality_problem quality_problem_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem
    ADD CONSTRAINT quality_problem_pkey PRIMARY KEY (id);


--
-- TOC entry 3377 (class 2606 OID 322195)
-- Name: quality_problem_project quality_problem_project_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem_project
    ADD CONSTRAINT quality_problem_project_pkey PRIMARY KEY (id);


--
-- TOC entry 3381 (class 2606 OID 322197)
-- Name: quality_problem_project quality_problem_project_quality_problem_id_proje_8701bfb2_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem_project
    ADD CONSTRAINT quality_problem_project_quality_problem_id_proje_8701bfb2_uniq UNIQUE (quality_problem_id, project_id);


--
-- TOC entry 3383 (class 2606 OID 322199)
-- Name: quality_problem_reviews quality_problem_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem_reviews
    ADD CONSTRAINT quality_problem_reviews_pkey PRIMARY KEY (id);


--
-- TOC entry 3386 (class 2606 OID 322201)
-- Name: quality_problem_reviews quality_problem_reviews_qualityproblem_id_review_c47d400f_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem_reviews
    ADD CONSTRAINT quality_problem_reviews_qualityproblem_id_review_c47d400f_uniq UNIQUE (qualityproblem_id, review_id);


--
-- TOC entry 3393 (class 2606 OID 322203)
-- Name: review_context_components review_context_component_review_id_contextcompone_cdfaa2da_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_context_components
    ADD CONSTRAINT review_context_component_review_id_contextcompone_cdfaa2da_uniq UNIQUE (review_id, contextcomponent_id);


--
-- TOC entry 3396 (class 2606 OID 322205)
-- Name: review_context_components review_context_components_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_context_components
    ADD CONSTRAINT review_context_components_pkey PRIMARY KEY (id);


--
-- TOC entry 3389 (class 2606 OID 322207)
-- Name: review review_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review
    ADD CONSTRAINT review_pkey PRIMARY KEY (id);


--
-- TOC entry 3399 (class 2606 OID 322209)
-- Name: review_quality_problems review_quality_problems_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_quality_problems
    ADD CONSTRAINT review_quality_problems_pkey PRIMARY KEY (id);


--
-- TOC entry 3403 (class 2606 OID 322211)
-- Name: review_quality_problems review_quality_problems_review_id_qualityproblem_6295882c_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_quality_problems
    ADD CONSTRAINT review_quality_problems_review_id_qualityproblem_6295882c_uniq UNIQUE (review_id, qualityproblem_id);


--
-- TOC entry 3405 (class 2606 OID 322213)
-- Name: system_requirement system_requirement_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_requirement
    ADD CONSTRAINT system_requirement_pkey PRIMARY KEY (contextcomponent_ptr_id);


--
-- TOC entry 3410 (class 2606 OID 322215)
-- Name: task_at_hand_other_data task_at_hand_other_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_other_data
    ADD CONSTRAINT task_at_hand_other_data_pkey PRIMARY KEY (id);


--
-- TOC entry 3413 (class 2606 OID 322217)
-- Name: task_at_hand_other_data task_at_hand_other_data_taskathand_id_otherdata__c563cde9_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_other_data
    ADD CONSTRAINT task_at_hand_other_data_taskathand_id_otherdata__c563cde9_uniq UNIQUE (taskathand_id, otherdata_id);


--
-- TOC entry 3407 (class 2606 OID 322219)
-- Name: task_at_hand task_at_hand_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand
    ADD CONSTRAINT task_at_hand_pkey PRIMARY KEY (contextcomponent_ptr_id);


--
-- TOC entry 3415 (class 2606 OID 322221)
-- Name: task_at_hand_system_requirements task_at_hand_system_requ_taskathand_id_systemrequ_69f05663_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_system_requirements
    ADD CONSTRAINT task_at_hand_system_requ_taskathand_id_systemrequ_69f05663_uniq UNIQUE (taskathand_id, systemrequirement_id);


--
-- TOC entry 3417 (class 2606 OID 322223)
-- Name: task_at_hand_system_requirements task_at_hand_system_requirements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_system_requirements
    ADD CONSTRAINT task_at_hand_system_requirements_pkey PRIMARY KEY (id);


--
-- TOC entry 3421 (class 2606 OID 322225)
-- Name: task_at_hand_user_types task_at_hand_user_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_user_types
    ADD CONSTRAINT task_at_hand_user_types_pkey PRIMARY KEY (id);


--
-- TOC entry 3424 (class 2606 OID 322227)
-- Name: task_at_hand_user_types task_at_hand_user_types_taskathand_id_usertype_id_a159b864_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_user_types
    ADD CONSTRAINT task_at_hand_user_types_taskathand_id_usertype_id_a159b864_uniq UNIQUE (taskathand_id, usertype_id);


--
-- TOC entry 3432 (class 2606 OID 322229)
-- Name: user_data user_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_data
    ADD CONSTRAINT user_data_pkey PRIMARY KEY (id);


--
-- TOC entry 3436 (class 2606 OID 322231)
-- Name: user_groups user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_pkey PRIMARY KEY (id);


--
-- TOC entry 3439 (class 2606 OID 322233)
-- Name: user_groups user_groups_user_id_group_id_40beef00_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_user_id_group_id_40beef00_uniq UNIQUE (user_id, group_id);


--
-- TOC entry 3427 (class 2606 OID 322235)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- TOC entry 3441 (class 2606 OID 322237)
-- Name: user_type user_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_type
    ADD CONSTRAINT user_type_pkey PRIMARY KEY (contextcomponent_ptr_id);


--
-- TOC entry 3444 (class 2606 OID 322239)
-- Name: user_user_permissions user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_user_permissions
    ADD CONSTRAINT user_user_permissions_pkey PRIMARY KEY (id);


--
-- TOC entry 3447 (class 2606 OID 322241)
-- Name: user_user_permissions user_user_permissions_user_id_permission_id_7dc6e2e0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_user_permissions
    ADD CONSTRAINT user_user_permissions_user_id_permission_id_7dc6e2e0_uniq UNIQUE (user_id, permission_id);


--
-- TOC entry 3430 (class 2606 OID 322243)
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- TOC entry 3230 (class 1259 OID 322244)
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- TOC entry 3235 (class 1259 OID 322245)
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- TOC entry 3238 (class 1259 OID 322246)
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- TOC entry 3241 (class 1259 OID 322247)
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- TOC entry 3253 (class 1259 OID 322248)
-- Name: context_component_project_stage_id_79ecc49f; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX context_component_project_stage_id_79ecc49f ON public.context_component USING btree (project_stage_id);


--
-- TOC entry 3256 (class 1259 OID 322249)
-- Name: context_context_components_context_id_0568cb54; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX context_context_components_context_id_0568cb54 ON public.context_context_components USING btree (context_id);


--
-- TOC entry 3257 (class 1259 OID 322250)
-- Name: context_context_components_contextcomponent_id_3d5588ac; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX context_context_components_contextcomponent_id_3d5588ac ON public.context_context_components USING btree (contextcomponent_id);


--
-- TOC entry 3250 (class 1259 OID 322251)
-- Name: context_previous_version_id_5d7f0825; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX context_previous_version_id_5d7f0825 ON public.context USING btree (previous_version_id);


--
-- TOC entry 3264 (class 1259 OID 322252)
-- Name: data_filtering_task_at_hand_id_fdb6b777; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX data_filtering_task_at_hand_id_fdb6b777 ON public.data_filtering USING btree (task_at_hand_id);


--
-- TOC entry 3270 (class 1259 OID 322253)
-- Name: data_profiling_context_components_contextcomponent_id_b3bbff45; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX data_profiling_context_components_contextcomponent_id_b3bbff45 ON public.data_profiling_context_components USING btree (contextcomponent_id);


--
-- TOC entry 3271 (class 1259 OID 322254)
-- Name: data_profiling_context_components_dataprofiling_id_268c37c6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX data_profiling_context_components_dataprofiling_id_268c37c6 ON public.data_profiling_context_components USING btree (dataprofiling_id);


--
-- TOC entry 3267 (class 1259 OID 322255)
-- Name: data_profiling_project_id_c626fbda; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX data_profiling_project_id_c626fbda ON public.data_profiling USING btree (project_id);


--
-- TOC entry 3278 (class 1259 OID 322256)
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- TOC entry 3281 (class 1259 OID 322257)
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- TOC entry 3288 (class 1259 OID 322258)
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- TOC entry 3291 (class 1259 OID 322259)
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- TOC entry 3296 (class 1259 OID 322260)
-- Name: dq_model_previous_version_id_84f9b629; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dq_model_previous_version_id_84f9b629 ON public.dqmodel_dqmodel USING btree (previous_version_id);


--
-- TOC entry 3302 (class 1259 OID 322261)
-- Name: dq_requirement_data_filtering_datafiltering_id_75a4216a; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dq_requirement_data_filtering_datafiltering_id_75a4216a ON public.dq_requirement_data_filtering USING btree (datafiltering_id);


--
-- TOC entry 3303 (class 1259 OID 322262)
-- Name: dq_requirement_data_filtering_dqrequirement_id_d62fdcfe; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dq_requirement_data_filtering_dqrequirement_id_d62fdcfe ON public.dq_requirement_data_filtering USING btree (dqrequirement_id);


--
-- TOC entry 3299 (class 1259 OID 322263)
-- Name: dq_requirement_user_type_id_0776391c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dq_requirement_user_type_id_0776391c ON public.dq_requirement USING btree (user_type_id);


--
-- TOC entry 3306 (class 1259 OID 322264)
-- Name: dqmodel_aggregationdqmethod_associatedTo_id_c7468269; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "dqmodel_aggregationdqmethod_associatedTo_id_c7468269" ON public.dqmodel_aggregationdqmethod USING btree ("associatedTo_id");


--
-- TOC entry 3309 (class 1259 OID 322265)
-- Name: dqmodel_dqdimensionbase_name_d09ae267_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqdimensionbase_name_d09ae267_like ON public.dqmodel_dqdimensionbase USING btree (name varchar_pattern_ops);


--
-- TOC entry 3314 (class 1259 OID 322266)
-- Name: dqmodel_dqfactorbase_facetOf_id_f109aabc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "dqmodel_dqfactorbase_facetOf_id_f109aabc" ON public.dqmodel_dqfactorbase USING btree ("facetOf_id");


--
-- TOC entry 3315 (class 1259 OID 322267)
-- Name: dqmodel_dqfactorbase_name_f871cf35_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqfactorbase_name_f871cf35_like ON public.dqmodel_dqfactorbase USING btree (name varchar_pattern_ops);


--
-- TOC entry 3320 (class 1259 OID 322268)
-- Name: dqmodel_dqmethodbase_implements_id_b79b0a70; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmethodbase_implements_id_b79b0a70 ON public.dqmodel_dqmethodbase USING btree (implements_id);


--
-- TOC entry 3321 (class 1259 OID 322269)
-- Name: dqmodel_dqmethodbase_name_f8c656b5_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmethodbase_name_f8c656b5_like ON public.dqmodel_dqmethodbase USING btree (name varchar_pattern_ops);


--
-- TOC entry 3326 (class 1259 OID 322270)
-- Name: dqmodel_dqmetricbase_measures_id_c354ef8d; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmetricbase_measures_id_c354ef8d ON public.dqmodel_dqmetricbase USING btree (measures_id);


--
-- TOC entry 3327 (class 1259 OID 322271)
-- Name: dqmodel_dqmetricbase_name_be038f8b_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmetricbase_name_be038f8b_like ON public.dqmodel_dqmetricbase USING btree (name varchar_pattern_ops);


--
-- TOC entry 3332 (class 1259 OID 322272)
-- Name: dqmodel_dqmodeldimension_dimension_base_id_f7ad0c0f; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodeldimension_dimension_base_id_f7ad0c0f ON public.dqmodel_dqmodeldimension USING btree (dimension_base_id);


--
-- TOC entry 3333 (class 1259 OID 322273)
-- Name: dqmodel_dqmodeldimension_dq_model_id_bf36bd38; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodeldimension_dq_model_id_bf36bd38 ON public.dqmodel_dqmodeldimension USING btree (dq_model_id);


--
-- TOC entry 3336 (class 1259 OID 322274)
-- Name: dqmodel_dqmodelfactor_dimension_id_ae4e1dfa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodelfactor_dimension_id_ae4e1dfa ON public.dqmodel_dqmodelfactor USING btree (dimension_id);


--
-- TOC entry 3337 (class 1259 OID 322275)
-- Name: dqmodel_dqmodelfactor_dq_model_id_d478a234; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodelfactor_dq_model_id_d478a234 ON public.dqmodel_dqmodelfactor USING btree (dq_model_id);


--
-- TOC entry 3338 (class 1259 OID 322276)
-- Name: dqmodel_dqmodelfactor_factor_base_id_f1fc3728; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodelfactor_factor_base_id_f1fc3728 ON public.dqmodel_dqmodelfactor USING btree (factor_base_id);


--
-- TOC entry 3341 (class 1259 OID 322277)
-- Name: dqmodel_dqmodelmethod_dq_model_id_08e7e457; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodelmethod_dq_model_id_08e7e457 ON public.dqmodel_dqmodelmethod USING btree (dq_model_id);


--
-- TOC entry 3342 (class 1259 OID 322278)
-- Name: dqmodel_dqmodelmethod_method_base_id_f28288df; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodelmethod_method_base_id_f28288df ON public.dqmodel_dqmodelmethod USING btree (method_base_id);


--
-- TOC entry 3343 (class 1259 OID 322279)
-- Name: dqmodel_dqmodelmethod_metric_id_9ea80baa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodelmethod_metric_id_9ea80baa ON public.dqmodel_dqmodelmethod USING btree (metric_id);


--
-- TOC entry 3346 (class 1259 OID 322280)
-- Name: dqmodel_dqmodelmetric_dq_model_id_a5c763ee; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodelmetric_dq_model_id_a5c763ee ON public.dqmodel_dqmodelmetric USING btree (dq_model_id);


--
-- TOC entry 3347 (class 1259 OID 322281)
-- Name: dqmodel_dqmodelmetric_factor_id_72b6cfc0; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodelmetric_factor_id_72b6cfc0 ON public.dqmodel_dqmodelmetric USING btree (factor_id);


--
-- TOC entry 3348 (class 1259 OID 322282)
-- Name: dqmodel_dqmodelmetric_metric_base_id_8c3491e7; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX dqmodel_dqmodelmetric_metric_base_id_8c3491e7 ON public.dqmodel_dqmodelmetric USING btree (metric_base_id);


--
-- TOC entry 3351 (class 1259 OID 322283)
-- Name: dqmodel_measurementdqmethod_associatedTo_id_dbc62005; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX "dqmodel_measurementdqmethod_associatedTo_id_dbc62005" ON public.dqmodel_measurementdqmethod USING btree ("associatedTo_id");


--
-- TOC entry 3362 (class 1259 OID 322284)
-- Name: project_context_id_d164131d; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX project_context_id_d164131d ON public.project USING btree (context_id);


--
-- TOC entry 3363 (class 1259 OID 322285)
-- Name: project_data_at_hand_id_a70664f2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX project_data_at_hand_id_a70664f2 ON public.project USING btree (data_at_hand_id);


--
-- TOC entry 3364 (class 1259 OID 322286)
-- Name: project_dqmodel_version_id_2fbfcce8; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX project_dqmodel_version_id_2fbfcce8 ON public.project USING btree (dqmodel_version_id);


--
-- TOC entry 3372 (class 1259 OID 322287)
-- Name: project_stage_project_id_f5df8bb7; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX project_stage_project_id_f5df8bb7 ON public.project_stage USING btree (project_id);


--
-- TOC entry 3369 (class 1259 OID 322288)
-- Name: project_user_id_b5fbb914; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX project_user_id_b5fbb914 ON public.project USING btree (user_id);


--
-- TOC entry 3378 (class 1259 OID 322289)
-- Name: quality_problem_project_project_id_f34e6742; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX quality_problem_project_project_id_f34e6742 ON public.quality_problem_project USING btree (project_id);


--
-- TOC entry 3379 (class 1259 OID 322290)
-- Name: quality_problem_project_quality_problem_id_733a1bdc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX quality_problem_project_quality_problem_id_733a1bdc ON public.quality_problem_project USING btree (quality_problem_id);


--
-- TOC entry 3375 (class 1259 OID 322291)
-- Name: quality_problem_project_stage_id_8e52d78f; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX quality_problem_project_stage_id_8e52d78f ON public.quality_problem USING btree (project_stage_id);


--
-- TOC entry 3384 (class 1259 OID 322292)
-- Name: quality_problem_reviews_qualityproblem_id_91ae9f7d; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX quality_problem_reviews_qualityproblem_id_91ae9f7d ON public.quality_problem_reviews USING btree (qualityproblem_id);


--
-- TOC entry 3387 (class 1259 OID 322293)
-- Name: quality_problem_reviews_review_id_d4528d9b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX quality_problem_reviews_review_id_d4528d9b ON public.quality_problem_reviews USING btree (review_id);


--
-- TOC entry 3394 (class 1259 OID 322294)
-- Name: review_context_components_contextcomponent_id_dd8c3535; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX review_context_components_contextcomponent_id_dd8c3535 ON public.review_context_components USING btree (contextcomponent_id);


--
-- TOC entry 3397 (class 1259 OID 322295)
-- Name: review_context_components_review_id_99533dd7; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX review_context_components_review_id_99533dd7 ON public.review_context_components USING btree (review_id);


--
-- TOC entry 3390 (class 1259 OID 322296)
-- Name: review_project_id_278ebdf1; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX review_project_id_278ebdf1 ON public.review USING btree (project_id);


--
-- TOC entry 3400 (class 1259 OID 322297)
-- Name: review_quality_problems_qualityproblem_id_7faf25cf; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX review_quality_problems_qualityproblem_id_7faf25cf ON public.review_quality_problems USING btree (qualityproblem_id);


--
-- TOC entry 3401 (class 1259 OID 322298)
-- Name: review_quality_problems_review_id_f4c8794f; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX review_quality_problems_review_id_f4c8794f ON public.review_quality_problems USING btree (review_id);


--
-- TOC entry 3391 (class 1259 OID 322299)
-- Name: review_user_id_1520d914; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX review_user_id_1520d914 ON public.review USING btree (user_id);


--
-- TOC entry 3408 (class 1259 OID 322300)
-- Name: task_at_hand_other_data_otherdata_id_bd2c7de5; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_at_hand_other_data_otherdata_id_bd2c7de5 ON public.task_at_hand_other_data USING btree (otherdata_id);


--
-- TOC entry 3411 (class 1259 OID 322301)
-- Name: task_at_hand_other_data_taskathand_id_e06c6958; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_at_hand_other_data_taskathand_id_e06c6958 ON public.task_at_hand_other_data USING btree (taskathand_id);


--
-- TOC entry 3418 (class 1259 OID 322302)
-- Name: task_at_hand_system_requirements_systemrequirement_id_22bd65ab; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_at_hand_system_requirements_systemrequirement_id_22bd65ab ON public.task_at_hand_system_requirements USING btree (systemrequirement_id);


--
-- TOC entry 3419 (class 1259 OID 322303)
-- Name: task_at_hand_system_requirements_taskathand_id_8db2f834; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_at_hand_system_requirements_taskathand_id_8db2f834 ON public.task_at_hand_system_requirements USING btree (taskathand_id);


--
-- TOC entry 3422 (class 1259 OID 322304)
-- Name: task_at_hand_user_types_taskathand_id_60a214f2; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_at_hand_user_types_taskathand_id_60a214f2 ON public.task_at_hand_user_types USING btree (taskathand_id);


--
-- TOC entry 3425 (class 1259 OID 322305)
-- Name: task_at_hand_user_types_usertype_id_e776ccc8; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX task_at_hand_user_types_usertype_id_e776ccc8 ON public.task_at_hand_user_types USING btree (usertype_id);


--
-- TOC entry 3226 (class 1259 OID 322306)
-- Name: uploaded_file_file_type_id_d37ce33a; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX uploaded_file_file_type_id_d37ce33a ON public.uploaded_file USING btree (file_type_id);


--
-- TOC entry 3227 (class 1259 OID 322307)
-- Name: uploaded_file_review_id_fc9e222c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX uploaded_file_review_id_fc9e222c ON public.uploaded_file USING btree (review_id);


--
-- TOC entry 3433 (class 1259 OID 322308)
-- Name: user_data_user_type_id_fed5d517; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_data_user_type_id_fed5d517 ON public.user_data USING btree (user_type_id);


--
-- TOC entry 3434 (class 1259 OID 322309)
-- Name: user_groups_group_id_b76f8aba; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_groups_group_id_b76f8aba ON public.user_groups USING btree (group_id);


--
-- TOC entry 3437 (class 1259 OID 322310)
-- Name: user_groups_user_id_abaea130; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_groups_user_id_abaea130 ON public.user_groups USING btree (user_id);


--
-- TOC entry 3442 (class 1259 OID 322311)
-- Name: user_user_permissions_permission_id_9deb68a3; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_user_permissions_permission_id_9deb68a3 ON public.user_user_permissions USING btree (permission_id);


--
-- TOC entry 3445 (class 1259 OID 322312)
-- Name: user_user_permissions_user_id_ed4a47ea; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_user_permissions_user_id_ed4a47ea ON public.user_user_permissions USING btree (user_id);


--
-- TOC entry 3428 (class 1259 OID 322313)
-- Name: user_username_cf016618_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX user_username_cf016618_like ON public."user" USING btree (username varchar_pattern_ops);


--
-- TOC entry 3450 (class 2606 OID 322314)
-- Name: application_domain application_domain_contextcomponent_ptr_0d790bbb_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.application_domain
    ADD CONSTRAINT application_domain_contextcomponent_ptr_0d790bbb_fk_context_c FOREIGN KEY (contextcomponent_ptr_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3451 (class 2606 OID 322319)
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3452 (class 2606 OID 322324)
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3453 (class 2606 OID 322329)
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3454 (class 2606 OID 322334)
-- Name: business_rule business_rule_contextcomponent_ptr_ef288458_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.business_rule
    ADD CONSTRAINT business_rule_contextcomponent_ptr_ef288458_fk_context_c FOREIGN KEY (contextcomponent_ptr_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3456 (class 2606 OID 322339)
-- Name: context_component context_component_project_stage_id_79ecc49f_fk_project_stage_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context_component
    ADD CONSTRAINT context_component_project_stage_id_79ecc49f_fk_project_stage_id FOREIGN KEY (project_stage_id) REFERENCES public.project_stage(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3457 (class 2606 OID 322344)
-- Name: context_context_components context_context_comp_contextcomponent_id_3d5588ac_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context_context_components
    ADD CONSTRAINT context_context_comp_contextcomponent_id_3d5588ac_fk_context_c FOREIGN KEY (contextcomponent_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3458 (class 2606 OID 322349)
-- Name: context_context_components context_context_components_context_id_0568cb54_fk_context_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context_context_components
    ADD CONSTRAINT context_context_components_context_id_0568cb54_fk_context_id FOREIGN KEY (context_id) REFERENCES public.context(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3455 (class 2606 OID 322354)
-- Name: context context_previous_version_id_5d7f0825_fk_context_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.context
    ADD CONSTRAINT context_previous_version_id_5d7f0825_fk_context_id FOREIGN KEY (previous_version_id) REFERENCES public.context(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3459 (class 2606 OID 322359)
-- Name: data_filtering data_filtering_contextcomponent_ptr_d6e577f1_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_filtering
    ADD CONSTRAINT data_filtering_contextcomponent_ptr_d6e577f1_fk_context_c FOREIGN KEY (contextcomponent_ptr_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3460 (class 2606 OID 322364)
-- Name: data_filtering data_filtering_task_at_hand_id_fdb6b777_fk_task_at_h; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_filtering
    ADD CONSTRAINT data_filtering_task_at_hand_id_fdb6b777_fk_task_at_h FOREIGN KEY (task_at_hand_id) REFERENCES public.task_at_hand(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3462 (class 2606 OID 322369)
-- Name: data_profiling_context_components data_profiling_conte_contextcomponent_id_b3bbff45_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_profiling_context_components
    ADD CONSTRAINT data_profiling_conte_contextcomponent_id_b3bbff45_fk_context_c FOREIGN KEY (contextcomponent_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3463 (class 2606 OID 322374)
-- Name: data_profiling_context_components data_profiling_conte_dataprofiling_id_268c37c6_fk_data_prof; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_profiling_context_components
    ADD CONSTRAINT data_profiling_conte_dataprofiling_id_268c37c6_fk_data_prof FOREIGN KEY (dataprofiling_id) REFERENCES public.data_profiling(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3461 (class 2606 OID 322379)
-- Name: data_profiling data_profiling_project_id_c626fbda_fk_project_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_profiling
    ADD CONSTRAINT data_profiling_project_id_c626fbda_fk_project_id FOREIGN KEY (project_id) REFERENCES public.project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3464 (class 2606 OID 322384)
-- Name: data_schema data_schema_data_at_hand_id_acdba179_fk_data_at_hand_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_schema
    ADD CONSTRAINT data_schema_data_at_hand_id_acdba179_fk_data_at_hand_id FOREIGN KEY (data_at_hand_id) REFERENCES public.data_at_hand(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3465 (class 2606 OID 322389)
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3466 (class 2606 OID 322394)
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_user_id FOREIGN KEY (user_id) REFERENCES public."user"(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3467 (class 2606 OID 322399)
-- Name: dq_metadata dq_metadata_contextcomponent_ptr_75fc3bb2_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dq_metadata
    ADD CONSTRAINT dq_metadata_contextcomponent_ptr_75fc3bb2_fk_context_c FOREIGN KEY (contextcomponent_ptr_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3468 (class 2606 OID 322404)
-- Name: dqmodel_dqmodel dq_model_previous_version_id_84f9b629_fk_dq_model_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodel
    ADD CONSTRAINT dq_model_previous_version_id_84f9b629_fk_dq_model_id FOREIGN KEY (previous_version_id) REFERENCES public.dqmodel_dqmodel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3469 (class 2606 OID 322409)
-- Name: dq_requirement dq_requirement_contextcomponent_ptr_de3d7c1e_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dq_requirement
    ADD CONSTRAINT dq_requirement_contextcomponent_ptr_de3d7c1e_fk_context_c FOREIGN KEY (contextcomponent_ptr_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3471 (class 2606 OID 322414)
-- Name: dq_requirement_data_filtering dq_requirement_data__datafiltering_id_75a4216a_fk_data_filt; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dq_requirement_data_filtering
    ADD CONSTRAINT dq_requirement_data__datafiltering_id_75a4216a_fk_data_filt FOREIGN KEY (datafiltering_id) REFERENCES public.data_filtering(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3472 (class 2606 OID 322419)
-- Name: dq_requirement_data_filtering dq_requirement_data__dqrequirement_id_d62fdcfe_fk_dq_requir; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dq_requirement_data_filtering
    ADD CONSTRAINT dq_requirement_data__dqrequirement_id_d62fdcfe_fk_dq_requir FOREIGN KEY (dqrequirement_id) REFERENCES public.dq_requirement(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3470 (class 2606 OID 322424)
-- Name: dq_requirement dq_requirement_user_type_id_0776391c_fk_user_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dq_requirement
    ADD CONSTRAINT dq_requirement_user_type_id_0776391c_fk_user_type FOREIGN KEY (user_type_id) REFERENCES public.user_type(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3473 (class 2606 OID 322429)
-- Name: dqmodel_aggregationdqmethod dqmodel_aggregationd_associatedTo_id_c7468269_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_aggregationdqmethod
    ADD CONSTRAINT "dqmodel_aggregationd_associatedTo_id_c7468269_fk_dqmodel_d" FOREIGN KEY ("associatedTo_id") REFERENCES public.dqmodel_dqmodelmethod(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3474 (class 2606 OID 322434)
-- Name: dqmodel_dqfactorbase dqmodel_dqfactorbase_facetOf_id_f109aabc_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqfactorbase
    ADD CONSTRAINT "dqmodel_dqfactorbase_facetOf_id_f109aabc_fk_dqmodel_d" FOREIGN KEY ("facetOf_id") REFERENCES public.dqmodel_dqdimensionbase(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3475 (class 2606 OID 322439)
-- Name: dqmodel_dqmethodbase dqmodel_dqmethodbase_implements_id_b79b0a70_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmethodbase
    ADD CONSTRAINT dqmodel_dqmethodbase_implements_id_b79b0a70_fk_dqmodel_d FOREIGN KEY (implements_id) REFERENCES public.dqmodel_dqmetricbase(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3476 (class 2606 OID 322444)
-- Name: dqmodel_dqmetricbase dqmodel_dqmetricbase_measures_id_c354ef8d_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmetricbase
    ADD CONSTRAINT dqmodel_dqmetricbase_measures_id_c354ef8d_fk_dqmodel_d FOREIGN KEY (measures_id) REFERENCES public.dqmodel_dqfactorbase(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3477 (class 2606 OID 322449)
-- Name: dqmodel_dqmodeldimension dqmodel_dqmodeldimen_dimension_base_id_f7ad0c0f_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodeldimension
    ADD CONSTRAINT dqmodel_dqmodeldimen_dimension_base_id_f7ad0c0f_fk_dqmodel_d FOREIGN KEY (dimension_base_id) REFERENCES public.dqmodel_dqdimensionbase(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3478 (class 2606 OID 322454)
-- Name: dqmodel_dqmodeldimension dqmodel_dqmodeldimen_dq_model_id_bf36bd38_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodeldimension
    ADD CONSTRAINT dqmodel_dqmodeldimen_dq_model_id_bf36bd38_fk_dqmodel_d FOREIGN KEY (dq_model_id) REFERENCES public.dqmodel_dqmodel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3479 (class 2606 OID 322459)
-- Name: dqmodel_dqmodelfactor dqmodel_dqmodelfacto_dimension_id_ae4e1dfa_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelfactor
    ADD CONSTRAINT dqmodel_dqmodelfacto_dimension_id_ae4e1dfa_fk_dqmodel_d FOREIGN KEY (dimension_id) REFERENCES public.dqmodel_dqmodeldimension(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3480 (class 2606 OID 322464)
-- Name: dqmodel_dqmodelfactor dqmodel_dqmodelfacto_dq_model_id_d478a234_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelfactor
    ADD CONSTRAINT dqmodel_dqmodelfacto_dq_model_id_d478a234_fk_dqmodel_d FOREIGN KEY (dq_model_id) REFERENCES public.dqmodel_dqmodel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3481 (class 2606 OID 322469)
-- Name: dqmodel_dqmodelfactor dqmodel_dqmodelfacto_factor_base_id_f1fc3728_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelfactor
    ADD CONSTRAINT dqmodel_dqmodelfacto_factor_base_id_f1fc3728_fk_dqmodel_d FOREIGN KEY (factor_base_id) REFERENCES public.dqmodel_dqfactorbase(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3482 (class 2606 OID 322474)
-- Name: dqmodel_dqmodelmethod dqmodel_dqmodelmetho_dq_model_id_08e7e457_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelmethod
    ADD CONSTRAINT dqmodel_dqmodelmetho_dq_model_id_08e7e457_fk_dqmodel_d FOREIGN KEY (dq_model_id) REFERENCES public.dqmodel_dqmodel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3483 (class 2606 OID 322479)
-- Name: dqmodel_dqmodelmethod dqmodel_dqmodelmetho_method_base_id_f28288df_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelmethod
    ADD CONSTRAINT dqmodel_dqmodelmetho_method_base_id_f28288df_fk_dqmodel_d FOREIGN KEY (method_base_id) REFERENCES public.dqmodel_dqmethodbase(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3484 (class 2606 OID 322484)
-- Name: dqmodel_dqmodelmethod dqmodel_dqmodelmetho_metric_id_9ea80baa_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelmethod
    ADD CONSTRAINT dqmodel_dqmodelmetho_metric_id_9ea80baa_fk_dqmodel_d FOREIGN KEY (metric_id) REFERENCES public.dqmodel_dqmodelmetric(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3485 (class 2606 OID 322489)
-- Name: dqmodel_dqmodelmetric dqmodel_dqmodelmetri_dq_model_id_a5c763ee_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelmetric
    ADD CONSTRAINT dqmodel_dqmodelmetri_dq_model_id_a5c763ee_fk_dqmodel_d FOREIGN KEY (dq_model_id) REFERENCES public.dqmodel_dqmodel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3486 (class 2606 OID 322494)
-- Name: dqmodel_dqmodelmetric dqmodel_dqmodelmetri_factor_id_72b6cfc0_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelmetric
    ADD CONSTRAINT dqmodel_dqmodelmetri_factor_id_72b6cfc0_fk_dqmodel_d FOREIGN KEY (factor_id) REFERENCES public.dqmodel_dqmodelfactor(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3487 (class 2606 OID 322499)
-- Name: dqmodel_dqmodelmetric dqmodel_dqmodelmetri_metric_base_id_8c3491e7_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_dqmodelmetric
    ADD CONSTRAINT dqmodel_dqmodelmetri_metric_base_id_8c3491e7_fk_dqmodel_d FOREIGN KEY (metric_base_id) REFERENCES public.dqmodel_dqmetricbase(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3488 (class 2606 OID 322504)
-- Name: dqmodel_measurementdqmethod dqmodel_measurementd_associatedTo_id_dbc62005_fk_dqmodel_d; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dqmodel_measurementdqmethod
    ADD CONSTRAINT "dqmodel_measurementd_associatedTo_id_dbc62005_fk_dqmodel_d" FOREIGN KEY ("associatedTo_id") REFERENCES public.dqmodel_dqmodelmethod(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3489 (class 2606 OID 322509)
-- Name: other_data other_data_contextcomponent_ptr_fd1d333e_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.other_data
    ADD CONSTRAINT other_data_contextcomponent_ptr_fd1d333e_fk_context_c FOREIGN KEY (contextcomponent_ptr_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3490 (class 2606 OID 322514)
-- Name: other_metadata other_metadata_contextcomponent_ptr_84cc90e6_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.other_metadata
    ADD CONSTRAINT other_metadata_contextcomponent_ptr_84cc90e6_fk_context_c FOREIGN KEY (contextcomponent_ptr_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3491 (class 2606 OID 322519)
-- Name: project project_context_id_d164131d_fk_context_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_context_id_d164131d_fk_context_id FOREIGN KEY (context_id) REFERENCES public.context(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3492 (class 2606 OID 322524)
-- Name: project project_data_at_hand_id_a70664f2_fk_data_at_hand_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_data_at_hand_id_a70664f2_fk_data_at_hand_id FOREIGN KEY (data_at_hand_id) REFERENCES public.data_at_hand(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3493 (class 2606 OID 322529)
-- Name: project project_dqmodel_version_id_2fbfcce8_fk_dq_model_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_dqmodel_version_id_2fbfcce8_fk_dq_model_id FOREIGN KEY (dqmodel_version_id) REFERENCES public.dqmodel_dqmodel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3494 (class 2606 OID 322534)
-- Name: project project_estimation_id_5dfbca2d_fk_estimation_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_estimation_id_5dfbca2d_fk_estimation_id FOREIGN KEY (estimation_id) REFERENCES public.estimation(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3496 (class 2606 OID 322539)
-- Name: project_stage project_stage_project_id_f5df8bb7_fk_project_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_stage
    ADD CONSTRAINT project_stage_project_id_f5df8bb7_fk_project_id FOREIGN KEY (project_id) REFERENCES public.project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3495 (class 2606 OID 322544)
-- Name: project project_user_id_b5fbb914_fk_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project
    ADD CONSTRAINT project_user_id_b5fbb914_fk_user_id FOREIGN KEY (user_id) REFERENCES public."user"(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3498 (class 2606 OID 322549)
-- Name: quality_problem_project quality_problem_proj_quality_problem_id_733a1bdc_fk_quality_p; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem_project
    ADD CONSTRAINT quality_problem_proj_quality_problem_id_733a1bdc_fk_quality_p FOREIGN KEY (quality_problem_id) REFERENCES public.quality_problem(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3499 (class 2606 OID 322554)
-- Name: quality_problem_project quality_problem_project_project_id_f34e6742_fk_project_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem_project
    ADD CONSTRAINT quality_problem_project_project_id_f34e6742_fk_project_id FOREIGN KEY (project_id) REFERENCES public.project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3497 (class 2606 OID 322559)
-- Name: quality_problem quality_problem_project_stage_id_8e52d78f_fk_project_stage_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem
    ADD CONSTRAINT quality_problem_project_stage_id_8e52d78f_fk_project_stage_id FOREIGN KEY (project_stage_id) REFERENCES public.project_stage(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3500 (class 2606 OID 322564)
-- Name: quality_problem_reviews quality_problem_revi_qualityproblem_id_91ae9f7d_fk_quality_p; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem_reviews
    ADD CONSTRAINT quality_problem_revi_qualityproblem_id_91ae9f7d_fk_quality_p FOREIGN KEY (qualityproblem_id) REFERENCES public.quality_problem(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3501 (class 2606 OID 322569)
-- Name: quality_problem_reviews quality_problem_reviews_review_id_d4528d9b_fk_review_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_problem_reviews
    ADD CONSTRAINT quality_problem_reviews_review_id_d4528d9b_fk_review_id FOREIGN KEY (review_id) REFERENCES public.review(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3504 (class 2606 OID 322574)
-- Name: review_context_components review_context_compo_contextcomponent_id_dd8c3535_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_context_components
    ADD CONSTRAINT review_context_compo_contextcomponent_id_dd8c3535_fk_context_c FOREIGN KEY (contextcomponent_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3505 (class 2606 OID 322579)
-- Name: review_context_components review_context_components_review_id_99533dd7_fk_review_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_context_components
    ADD CONSTRAINT review_context_components_review_id_99533dd7_fk_review_id FOREIGN KEY (review_id) REFERENCES public.review(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3502 (class 2606 OID 322584)
-- Name: review review_project_id_278ebdf1_fk_project_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review
    ADD CONSTRAINT review_project_id_278ebdf1_fk_project_id FOREIGN KEY (project_id) REFERENCES public.project(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3506 (class 2606 OID 322589)
-- Name: review_quality_problems review_quality_probl_qualityproblem_id_7faf25cf_fk_quality_p; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_quality_problems
    ADD CONSTRAINT review_quality_probl_qualityproblem_id_7faf25cf_fk_quality_p FOREIGN KEY (qualityproblem_id) REFERENCES public.quality_problem(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3507 (class 2606 OID 322594)
-- Name: review_quality_problems review_quality_problems_review_id_f4c8794f_fk_review_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review_quality_problems
    ADD CONSTRAINT review_quality_problems_review_id_f4c8794f_fk_review_id FOREIGN KEY (review_id) REFERENCES public.review(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3503 (class 2606 OID 322599)
-- Name: review review_user_id_1520d914_fk_user_data_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.review
    ADD CONSTRAINT review_user_id_1520d914_fk_user_data_id FOREIGN KEY (user_id) REFERENCES public.user_data(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3508 (class 2606 OID 322604)
-- Name: system_requirement system_requirement_contextcomponent_ptr_23659feb_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_requirement
    ADD CONSTRAINT system_requirement_contextcomponent_ptr_23659feb_fk_context_c FOREIGN KEY (contextcomponent_ptr_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3509 (class 2606 OID 322609)
-- Name: task_at_hand task_at_hand_contextcomponent_ptr_6093bc41_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand
    ADD CONSTRAINT task_at_hand_contextcomponent_ptr_6093bc41_fk_context_c FOREIGN KEY (contextcomponent_ptr_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3510 (class 2606 OID 322614)
-- Name: task_at_hand_other_data task_at_hand_other_d_otherdata_id_bd2c7de5_fk_other_dat; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_other_data
    ADD CONSTRAINT task_at_hand_other_d_otherdata_id_bd2c7de5_fk_other_dat FOREIGN KEY (otherdata_id) REFERENCES public.other_data(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3511 (class 2606 OID 322619)
-- Name: task_at_hand_other_data task_at_hand_other_d_taskathand_id_e06c6958_fk_task_at_h; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_other_data
    ADD CONSTRAINT task_at_hand_other_d_taskathand_id_e06c6958_fk_task_at_h FOREIGN KEY (taskathand_id) REFERENCES public.task_at_hand(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3512 (class 2606 OID 322624)
-- Name: task_at_hand_system_requirements task_at_hand_system__systemrequirement_id_22bd65ab_fk_system_re; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_system_requirements
    ADD CONSTRAINT task_at_hand_system__systemrequirement_id_22bd65ab_fk_system_re FOREIGN KEY (systemrequirement_id) REFERENCES public.system_requirement(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3513 (class 2606 OID 322629)
-- Name: task_at_hand_system_requirements task_at_hand_system__taskathand_id_8db2f834_fk_task_at_h; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_system_requirements
    ADD CONSTRAINT task_at_hand_system__taskathand_id_8db2f834_fk_task_at_h FOREIGN KEY (taskathand_id) REFERENCES public.task_at_hand(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3514 (class 2606 OID 322634)
-- Name: task_at_hand_user_types task_at_hand_user_ty_taskathand_id_60a214f2_fk_task_at_h; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_user_types
    ADD CONSTRAINT task_at_hand_user_ty_taskathand_id_60a214f2_fk_task_at_h FOREIGN KEY (taskathand_id) REFERENCES public.task_at_hand(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3515 (class 2606 OID 322639)
-- Name: task_at_hand_user_types task_at_hand_user_ty_usertype_id_e776ccc8_fk_user_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_at_hand_user_types
    ADD CONSTRAINT task_at_hand_user_ty_usertype_id_e776ccc8_fk_user_type FOREIGN KEY (usertype_id) REFERENCES public.user_type(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3448 (class 2606 OID 322644)
-- Name: uploaded_file uploaded_file_file_type_id_d37ce33a_fk_file_type_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploaded_file
    ADD CONSTRAINT uploaded_file_file_type_id_d37ce33a_fk_file_type_id FOREIGN KEY (file_type_id) REFERENCES public.file_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3449 (class 2606 OID 322649)
-- Name: uploaded_file uploaded_file_review_id_fc9e222c_fk_review_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.uploaded_file
    ADD CONSTRAINT uploaded_file_review_id_fc9e222c_fk_review_id FOREIGN KEY (review_id) REFERENCES public.review(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3516 (class 2606 OID 322654)
-- Name: user_data user_data_user_type_id_fed5d517_fk_user_type; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_data
    ADD CONSTRAINT user_data_user_type_id_fed5d517_fk_user_type FOREIGN KEY (user_type_id) REFERENCES public.user_type(contextcomponent_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3517 (class 2606 OID 322659)
-- Name: user_groups user_groups_group_id_b76f8aba_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_group_id_b76f8aba_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3518 (class 2606 OID 322664)
-- Name: user_groups user_groups_user_id_abaea130_fk_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_user_id_abaea130_fk_user_id FOREIGN KEY (user_id) REFERENCES public."user"(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3519 (class 2606 OID 322669)
-- Name: user_type user_type_contextcomponent_ptr_59d3a875_fk_context_c; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_type
    ADD CONSTRAINT user_type_contextcomponent_ptr_59d3a875_fk_context_c FOREIGN KEY (contextcomponent_ptr_id) REFERENCES public.context_component(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3520 (class 2606 OID 322674)
-- Name: user_user_permissions user_user_permission_permission_id_9deb68a3_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_user_permissions
    ADD CONSTRAINT user_user_permission_permission_id_9deb68a3_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- TOC entry 3521 (class 2606 OID 322679)
-- Name: user_user_permissions user_user_permissions_user_id_ed4a47ea_fk_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_user_permissions
    ADD CONSTRAINT user_user_permissions_user_id_ed4a47ea_fk_user_id FOREIGN KEY (user_id) REFERENCES public."user"(id) DEFERRABLE INITIALLY DEFERRED;


-- Completed on 2025-09-06 21:31:21

--
-- PostgreSQL database dump complete
--

