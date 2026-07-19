--
-- PostgreSQL database dump
--

\restrict c6IsbhdzpL4hQeENd9KbWXFnHZhQYaQ3hBYbgM7N0xAsqbk6uUTV4SYUhDsHu28

-- Dumped from database version 15.18
-- Dumped by pg_dump version 15.18

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
-- Name: chaos_test; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chaos_test (
    id integer
);


ALTER TABLE public.chaos_test OWNER TO postgres;

--
-- Data for Name: chaos_test; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chaos_test (id) FROM stdin;
1
\.


--
-- PostgreSQL database dump complete
--

\unrestrict c6IsbhdzpL4hQeENd9KbWXFnHZhQYaQ3hBYbgM7N0xAsqbk6uUTV4SYUhDsHu28

