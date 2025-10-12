--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4 (Debian 15.4-2.pgdg120+1)
-- Dumped by pg_dump version 15.4 (Debian 15.4-2.pgdg120+1)

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

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: flashcards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.flashcards (
    id uuid NOT NULL,
    user_id uuid,
    session_id uuid NOT NULL,
    question text NOT NULL,
    answer text NOT NULL,
    source_type text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: long_term_memory; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.long_term_memory (
    id uuid NOT NULL,
    user_id uuid,
    summary text NOT NULL,
    meta_data json,
    embedding public.vector(768),
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.messages (
    id uuid NOT NULL,
    session_id uuid,
    sender character varying NOT NULL,
    content text NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now()
);


--
-- Name: notes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notes (
    id uuid NOT NULL,
    user_id uuid,
    session_id uuid NOT NULL,
    content text NOT NULL,
    source_type text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: plans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.plans (
    id integer NOT NULL,
    name character varying NOT NULL,
    description text,
    price double precision,
    message_limit integer,
    is_active boolean,
    notes_limit integer,
    flashcards_limit integer,
    billing_cycle character varying
);


--
-- Name: plans_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.plans_id_seq OWNED BY public.plans.id;


--
-- Name: quiz_attempts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quiz_attempts (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    session_id uuid NOT NULL,
    question_id uuid NOT NULL,
    user_answer text NOT NULL,
    verdict character varying NOT NULL,
    explanation text,
    score integer,
    created_at timestamp with time zone DEFAULT now(),
    attempt_number integer
);


--
-- Name: quizzes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quizzes (
    id uuid NOT NULL,
    session_id uuid NOT NULL,
    user_id uuid,
    question text,
    correct_answer character varying,
    options json,
    created_at timestamp with time zone DEFAULT now(),
    type character varying NOT NULL,
    correct_option character varying
);


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sessions (
    id uuid NOT NULL,
    user_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    title character varying
);


--
-- Name: studysessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.studysessions (
    id uuid NOT NULL,
    user_id uuid,
    title text NOT NULL,
    file_name text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    file_type text NOT NULL
);


--
-- Name: usage_limits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usage_limits (
    id integer NOT NULL,
    user_id uuid,
    date date,
    messages_used integer,
    notes_used integer,
    flashcards_used integer
);


--
-- Name: usage_limits_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usage_limits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usage_limits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usage_limits_id_seq OWNED BY public.usage_limits.id;


--
-- Name: user_subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_subscriptions (
    id integer NOT NULL,
    user_id uuid,
    plan_id integer,
    start_date timestamp without time zone,
    end_date timestamp without time zone,
    is_active boolean,
    razorpay_order_id character varying,
    razorpay_payment_id character varying,
    subscription_type character varying
);


--
-- Name: user_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_subscriptions_id_seq OWNED BY public.user_subscriptions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    username character varying NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying,
    plan character varying,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: plans id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plans ALTER COLUMN id SET DEFAULT nextval('public.plans_id_seq'::regclass);


--
-- Name: usage_limits id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_limits ALTER COLUMN id SET DEFAULT nextval('public.usage_limits_id_seq'::regclass);


--
-- Name: user_subscriptions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.user_subscriptions_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
caf581b00471
\.


--
-- Data for Name: flashcards; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.flashcards (id, user_id, session_id, question, answer, source_type, created_at) FROM stdin;
69b07382-f5cb-4d80-8523-97983129a35c	d0bb82c6-fff5-454e-a590-d83900072364	aebfe132-a9e4-4344-bc9f-95cd75a52327	What is the significance of the Preamble to the Indian Constitution?	- Acts as the **introductory statement**.\n- States the **objectives and guiding values**: Justice, Liberty, Equality, and Fraternity.	chat	2025-06-27 20:03:35.778347+00
c42ccc40-2b97-46b3-bc91-a8ea063ee49b	d0bb82c6-fff5-454e-a590-d83900072364	aebfe132-a9e4-4344-bc9f-95cd75a52327	What is the importance of Fundamental Rights?	- **Guaranteed by Part III** of the Constitution.\n- Protects **basic freedoms** of citizens against state action.	chat	2025-06-27 20:03:35.778655+00
8c69e5f2-b6be-458b-b0d9-468ad6804dbf	d0bb82c6-fff5-454e-a590-d83900072364	aebfe132-a9e4-4344-bc9f-95cd75a52327	Who is known as the ‘Father of the Indian Constitution’ and why?	- **Dr. B.R. Ambedkar**.\n- Chairman of the **Drafting Committee**.	chat	2025-06-27 20:03:35.7788+00
ae5c5f70-2ca5-48b4-a1ce-a8ae300fb1f3	d0bb82c6-fff5-454e-a590-d83900072364	aebfe132-a9e4-4344-bc9f-95cd75a52327	What makes the Indian Constitution a living document?	- Contains **provisions for amendments** under Article 368.\n- Can be **adapted to changing conditions** and needs of society.	chat	2025-06-27 20:03:35.778914+00
e2df2c22-a796-4b4e-ba7f-614cb0e8e2e9	d0bb82c6-fff5-454e-a590-d83900072364	aebfe132-a9e4-4344-bc9f-95cd75a52327	What is meant by a ‘Secular State’ as per the Indian Constitution?	- **No official state religion** recognized by the government.\n- Ensures **equal treatment of all religions** by the state.	chat	2025-06-27 20:03:35.779026+00
231ab5be-0b10-431f-8582-aa32435df86a	d0bb82c6-fff5-454e-a590-d83900072364	9e3f36fc-f15e-4c35-a279-df0c9408f658	What is the significance of the Preamble in the Indian Constitution?	- Acts as an **introductory statement** that outlines the objectives.\n- Highlights principles like **justice, liberty, equality**, and **fraternity**.	chat	2025-06-28 05:18:33.674421+00
c5cdd8e6-535b-4d6b-bed1-a15cb8e62bce	d0bb82c6-fff5-454e-a590-d83900072364	9e3f36fc-f15e-4c35-a279-df0c9408f658	Mention any two features of the Indian Constitution.	- It is a **written and lengthy document**.\n- Adopts the principle of **federalism with a unitary bias**.	chat	2025-06-28 05:18:33.67469+00
5a42651e-70ff-460d-942b-d0cc70c736e1	d0bb82c6-fff5-454e-a590-d83900072364	9e3f36fc-f15e-4c35-a279-df0c9408f658	What is the role of the President of India according to the Constitution?	- **Nominal executive head** of the State.\n- Functions are performed **on the aid and advice of the Council of Ministers**.	chat	2025-06-28 05:18:33.674829+00
14f6a0e3-0cf3-4088-a699-d576d36551a1	d0bb82c6-fff5-454e-a590-d83900072364	9e3f36fc-f15e-4c35-a279-df0c9408f658	Mention any two Fundamental Rights provided by the Indian Constitution.	- **Right to Equality (Article 14-18)** ensures equal treatment before law.\n- **Right to Freedom (Article 19-22)** guarantees personal and civil liberties.	chat	2025-06-28 05:18:33.674922+00
66d9a8ef-674e-4c87-8741-a56c0247cf76	d0bb82c6-fff5-454e-a590-d83900072364	9e3f36fc-f15e-4c35-a279-df0c9408f658	What do you understand by the term 'Secular' in the Indian Constitution?	- The State has **no official religion**.\n- Ensures **equal treatment of all religions** by the government.	chat	2025-06-28 05:18:33.674997+00
6356aae2-21b8-4673-929b-6c6b20509a4b	d0bb82c6-fff5-454e-a590-d83900072364	f276ebaa-f020-4124-a20e-b1662b99a3d5	What is the **G7 Summit**?	- Annual meeting of the **Group of Seven (G7)** major advanced economies.\n- Focuses on global economic issues, climate change, and security.	chat	2025-06-28 05:27:16.228169+00
b84b6420-1aae-410c-a759-164361798373	d0bb82c6-fff5-454e-a590-d83900072364	f276ebaa-f020-4124-a20e-b1662b99a3d5	Name any three member countries of the **G7**.	- **United States**\n- **Japan**\n- **Germany**	chat	2025-06-28 05:27:16.228418+00
6b8e1d86-5337-417c-9c19-fa82a3fe5dbc	d0bb82c6-fff5-454e-a590-d83900072364	f276ebaa-f020-4124-a20e-b1662b99a3d5	What is a key agenda often discussed at the **G7 Summit**?	- **Economic policy coordination**\n- **Climate change strategies**\n- **Global security and geopolitical tensions**	chat	2025-06-28 05:27:16.228508+00
8468ca91-9e04-4b6a-b171-de737fb81bab	d0bb82c6-fff5-454e-a590-d83900072364	f276ebaa-f020-4124-a20e-b1662b99a3d5	Which country hosted the **G7 Summit** in 2023?	- **Japan** hosted the G7 Summit in **Hiroshima** in 2023.\n- Leaders discussed issues like **Ukraine conflict** and **global health**.	chat	2025-06-28 05:27:16.228582+00
e5ca3302-b1c8-492e-8ffe-6053fcd42df7	d0bb82c6-fff5-454e-a590-d83900072364	f276ebaa-f020-4124-a20e-b1662b99a3d5	How are G7 Summit decisions implemented?	- Agreements are **non-binding**; rely on **member countries’ cooperation**.\n- Outcomes influence **global economic and political policies**.	chat	2025-06-28 05:27:16.228653+00
8ca3c7b6-1ab4-47e7-ac2e-564259020543	d0bb82c6-fff5-454e-a590-d83900072364	164ef914-246e-4c5d-9d38-cbee31a3a8a2	What are the primary features that make GenPOD a comprehensive solution for print-on-demand (POD) businesses?	- **AI-powered image generation, editing, and vectorization**\n- Integrates **Stable Diffusion** and **ControlNet** for precise image and edge control\n- Enables users to **create custom designs** for POD products,	file	2025-08-07 13:22:40.299563+00
6e958dea-a909-4f76-8537-0dcf21b30dd5	d0bb82c6-fff5-454e-a590-d83900072364	164ef914-246e-4c5d-9d38-cbee31a3a8a2	Briefly outline the main improvements made during GenPOD’s UI & functionality expansion phase.	- Developed a **user-friendly interface** with image upload and prompt-based generation\n- Added an **AI editor** for design modification and integrated **vectorization** tools (Autotrace, Inkscape CLI)\n- Enhanced the workflow for converting images to **SVG** for POD processing,	file	2025-08-07 13:22:40.299832+00
f096c9e8-0177-40be-b758-055f58464087	d0bb82c6-fff5-454e-a590-d83900072364	164ef914-246e-4c5d-9d38-cbee31a3a8a2	Describe how GenPOD advanced its design editing capabilities and the new functionalities introduced in this stage. (5 marks)	GenPOD significantly enhanced its editing capabilities by adopting **Konva.js**, which provided advanced, **layer-based editing** for users. This upgrade enabled key features such as **drag, resize, rotation, and color change** directly within the editor. Additionally, the introduction of a **WebSocket-based real-time pose editor** allowed for dynamic manipulation of **OpenPose keypoints**, making complex design adjustments more interactive and responsive for the end user.,	file	2025-08-07 13:22:40.299918+00
463020dd-0635-46d0-a2c7-dc71d91d1fc4	d0bb82c6-fff5-454e-a590-d83900072364	164ef914-246e-4c5d-9d38-cbee31a3a8a2	How does GenPOD utilize OpenPose and SAM to enhance design editing? (5 marks)	GenPOD integrates **OpenPose** to give users precise control over human poses in their designs by allowing direct adjustment of keypoints in real time. With the addition of the **Segment Anything Model (SAM)**, the platform can detect and manipulate multiple objects within an image, enabling users to edit and reposition components with accuracy and flexibility, thus greatly improving the customization capabilities essential for print-on-demand products.,	file	2025-08-07 13:22:40.299999+00
382d8ec3-1bda-4753-899a-4a97d2ae2f10	d0bb82c6-fff5-454e-a590-d83900072364	164ef914-246e-4c5d-9d38-cbee31a3a8a2	Summarize the main optimizations and current status of GenPOD as of the latest update. (5 marks)	Recent work on GenPOD focused on **optimizing the platform’s performance and fixing critical errors**, such as resolving issues with OpenPose outputs and preventing empty SVG files during vectorization. GPU usage was also optimized for better processing speed. As of now, **real-time pose editing is fully operational**, image generation is stable, and object positioning is flexible. The next development steps are aimed at refining object detection features and further enhancing the **editor’s UI** to offer a more seamless experience for users.	file	2025-08-07 13:22:40.30008+00
db11c055-9b66-4c1d-ad2e-308e6d98717e	d0bb82c6-fff5-454e-a590-d83900072364	915ada3a-2603-49df-a661-28b67085faf2	What is Natural Language Processing (NLP) and why is it challenging?	- **Natural Language Processing (NLP)** involves enabling computers to understand, interpret, and generate human language, both in text and speech form.  \n- **Challenges** include managing ambiguity, complex grammar structures, variability in expression, and understanding context, intent, and sentiment.\n\n,	file	2025-08-20 06:47:13.773282+00
5c1f89e7-7a7e-4949-9d24-d97848a560b4	d0bb82c6-fff5-454e-a590-d83900072364	915ada3a-2603-49df-a661-28b67085faf2	Explain the structure and phases of NLP in text preprocessing.	- NLP text preprocessing involves identifying the **structure of words and documents** by using **tokenization, morphological analysis, and sentence boundary detection**.  \n- Classes of NLP processing include **syntactic parsing** (like POS tagging, stemming, lemmatization) and **semantic parsing** (resolving meaning and ambiguity).\n\n,	file	2025-08-20 06:47:13.774489+00
cee93f74-654c-4583-9a7f-b4a4f102adf5	d0bb82c6-fff5-454e-a590-d83900072364	915ada3a-2603-49df-a661-28b67085faf2	What are some key applications of Natural Language Processing?	**NLP** is widely used in modern technology, with applications such as **sentiment analysis** for extracting opinions from text, **machine translation** for converting languages (e.g., Google Translate), **spam detection** for filtering emails, and **speech recognition** systems like Siri and Google Assistant. Other vital uses include **question answering**, **chatbots**, **spelling and grammar correction**, and **social media monitoring**.\n\n,	file	2025-08-20 06:47:13.77458+00
d0716052-b301-488c-b7f0-0d845e9d8148	d0bb82c6-fff5-454e-a590-d83900072364	915ada3a-2603-49df-a661-28b67085faf2	Describe the role and types of Language Models in NLP.	Language models play a crucial role in NLP for predicting the probability of word sequences and understanding textual context. Key types include the statistical **n-gram models** (which estimate the likelihood of word combinations, e.g., bigrams and trigrams), **class-based models**, **Maximum Entropy (MaxEnt) models**, and **neural network language models**. These models are evaluated on accuracy and are employed in crosslingual, multilingual tasks to enhance the performance and flexibility of NLP systems.\n\n,	file	2025-08-20 06:47:13.774658+00
b7c462f9-4720-4236-a76c-ed004ddae652	d0bb82c6-fff5-454e-a590-d83900072364	915ada3a-2603-49df-a661-28b67085faf2	How does NLP achieve semantic parsing and ambiguity resolution? (10 marks)	Semantic Parsing in NLP is the process of mapping natural language into a structured, machine-interpretable representation of meaning. This involves several essential components:  \n**1. Structural Ambiguity Resolution**: NLP uses parsing algorithms and models to identify and resolve ambiguities where multiple interpretations exist for a sentence (e.g., “I saw the man with the telescope”—is 'with the telescope' describing 'man' or 'saw'?).\n**2. Entity and Event Resolution**: Named entities (people, organizations, locations) and events are extracted by systems capable of distinguishing context, relationships, and roles within a sentence.\n**3. Predicate-Argument Structure**: Sentences are broken into predicates (verbs/actions) and their associated arguments (entities involved), which are connected to semantic roles for deeper comprehension.\n**4. Word Sense Disambiguation**: Algorithms identify the correct sense of polysemous words by examining context (e.g., "bank" as riverbank vs. financial institution).\n**5. Meaning Representation**: The final step is converting natural language into logical forms, semantic graphs, or querying languages that allow comprehensive understanding and downstream processing.  \nFor example, given the sentence "Mark and Emily married yesterday," semantic parsing extracts entities (Mark, Emily), identifies their relationship (spouse), and tags the event (marriage)—enabling machines to grasp the true meaning rather than just word order.\n\n,	file	2025-08-20 06:47:13.774733+00
\.


--
-- Data for Name: long_term_memory; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.long_term_memory (id, user_id, summary, meta_data, embedding, created_at) FROM stdin;
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.messages (id, session_id, sender, content, "timestamp") FROM stdin;
08805836-a131-4328-be1e-80ec931771de	920bbc7a-cc0e-4893-8aee-581b77842314	user	Helo test	2025-06-17 15:00:56.199387+00
8aaba6c4-c863-402d-bfa2-d9786f0774a1	920bbc7a-cc0e-4893-8aee-581b77842314	bot	- **Helo test** is a diagnostic procedure mainly used in **aerospace** or **marine engineering**.\n- It often refers to **testing helicopter (helo) components or systems**, such as engines or avionics, under controlled conditions.\n- Purpose: To ensure **safety**, **performance**, and **reliability** before operational deployment.	2025-06-17 15:00:56.199387+00
935a5829-3039-4c27-a5da-e3ecdf7aa047	920bbc7a-cc0e-4893-8aee-581b77842314	user	How are you	2025-06-17 15:01:12.803947+00
191a2eac-6c1c-4ac7-8559-0e881aaa1cea	920bbc7a-cc0e-4893-8aee-581b77842314	bot	- I'm just an **AI assistant**, so I don't have feelings.\n- But I'm always **ready to help** with your questions!	2025-06-17 15:01:12.803947+00
c42bb227-db51-40c1-9be8-b400365847a0	920bbc7a-cc0e-4893-8aee-581b77842314	user	GenPOD SaaS - Progress Summary\n1. Introduction\nGenPOD is an AI-powered print-on-demand (POD) design generator that allows users to create\ncustom designs using AI. The platform features image generation, editing, and vectorization\ncapabilities, making it a comprehensive solution for POD businesses.\n2. Initial Development\nWe started with basic image generation using Stable Diffusion and ControlNet.\nImplemented ControlNet (Canny, Lineart_Anime) for precise edge control.\n3. UI & Functionality Expansion\n• Developed an intuitive UI with image upload and prompt-based generation.\n• Integrated an AI-powered editor to allow users to modify their designs.\n• Implemented vectorization using Autotrace and later Inkscape CLI for SVG conversion.\n4. Transition to Advanced Editing\n• Shifted to Konva.js for better layer-based editing.\n• Enabled drag, resize, rotate, and color change features in the editor.\n• Implemented a WebSocket-based real-time pose editor for OpenPose keypoint manipulation.\n5. OpenPose & Object Editing\n• Added OpenPose integration for precise human pose control.\n• Implemented a real-time pose editor to allow users to adjust keypoints dynamically.\n• Integrated SAM (Segment Anything Model) to detect and manipulate multiple objects.\n6. Optimization & Error Fixes\n• Fixed issues where OpenPose was returning an image instead of keypoints.\n• Improved vectorization process to prevent empty SVG files.\n• Optimized GPU usage to enhance processing speed.\n7. Current Status\n• Real-time pose editing is fully functional.\n• Image generation is stable, with flexible object positioning.\n• Next steps include refining object detection and enhancing the editor’s UI.	2025-06-18 10:18:36.092856+00
776d2177-a749-4b68-a3df-59134f2bafbc	920bbc7a-cc0e-4893-8aee-581b77842314	bot	- **GenPOD** is an AI-powered print-on-demand platform with features like **image generation**, **vectorization**, and a **real-time pose editor**.\n- Progress includes integration of **Stable Diffusion**, **ControlNet**, advanced **OpenPose pose editing**, and a **layer-based editor** using **Konva.js**.\n- The platform now supports **real-time editing**, stable design generation, and is focusing on further **UI improvements** and **object detection** enhancements.	2025-06-18 10:18:36.092856+00
8c00b418-c44d-41c8-a6d1-d7bb6fcd7d74	920bbc7a-cc0e-4893-8aee-581b77842314	user	Summerize it	2025-06-20 18:35:28.965215+00
351ca7be-7066-44b6-bf56-012aea0adb53	920bbc7a-cc0e-4893-8aee-581b77842314	bot	- The extracted content is a **Python coroutine object**: `<coroutine object Redis.execute_command at 0x000001FB1BD4C260>`.\n- It indicates an **asynchronous call** to the `execute_command` method of a **Redis** client, but no actual result or data is shown.	2025-06-20 18:35:28.965215+00
e0443a89-3749-4498-bd6e-f6f649a3cbe0	920bbc7a-cc0e-4893-8aee-581b77842314	user	Summerize it	2025-06-20 18:49:43.372475+00
582b43e3-6a00-4ac3-af84-8085f5707578	920bbc7a-cc0e-4893-8aee-581b77842314	bot	- The text refers to a **Python coroutine object** used for **asynchronous operations** with Redis: `<coroutine object Redis.execute_command at ...>`.\n- It shows a **pending operation**; no actual data or result is displayed, only the representation of the coroutine.	2025-06-20 18:49:43.372475+00
0c0af945-5f64-4f4e-9a4f-e666602ffe70	920bbc7a-cc0e-4893-8aee-581b77842314	user	Summarize it	2025-06-20 18:56:49.466125+00
53db2b47-ebe1-42f5-9a34-3f11aef558aa	920bbc7a-cc0e-4893-8aee-581b77842314	bot	- The text refers to a **Python coroutine object** used for **asynchronous Redis operations**.\n- It indicates a **pending task** (e.g., a database command) without showing any result or data.	2025-06-20 18:56:49.466125+00
54cb8ed5-afde-4d65-97ac-56a3ae3d293b	920bbc7a-cc0e-4893-8aee-581b77842314	user	Sum it up	2025-06-20 18:59:50.268847+00
39c861e6-60a0-40d3-8d93-6d812c9ebef1	920bbc7a-cc0e-4893-8aee-581b77842314	bot	- The text describes a **Python coroutine object** for **asynchronous Redis commands**.\n- It shows a **pending action**—no result, just the coroutine awaiting execution.	2025-06-20 18:59:50.268847+00
8c20bbbc-f24f-4f39-828d-923053c02c94	920bbc7a-cc0e-4893-8aee-581b77842314	user	I want a summary	2025-06-20 19:10:32.365936+00
e9f8c5ed-a2ea-4d9e-bb0e-3888fc8c052e	920bbc7a-cc0e-4893-8aee-581b77842314	bot	- The text is about a **Python coroutine object** used for **asynchronous Redis operations**.\n- It represents a **pending task** that hasn't completed or returned any data yet.	2025-06-20 19:10:32.365936+00
6217ae6d-d1f5-41cf-b09c-81cfdba00c17	920bbc7a-cc0e-4893-8aee-581b77842314	user	Sum it up	2025-06-20 19:23:29.373078+00
7d589171-4b55-41e6-bc61-ee1c1bd30326	920bbc7a-cc0e-4893-8aee-581b77842314	bot	- The text is about a **Python coroutine** object for **asynchronous Redis operations**.\n- It represents a **pending task** that hasn't completed or returned results yet.	2025-06-20 19:23:29.373078+00
c5975ad4-bf79-4f29-88d8-8261c93f17c1	920bbc7a-cc0e-4893-8aee-581b77842314	user	I want a summary	2025-06-20 19:32:00.088563+00
c5f793a1-ae1f-49a5-bdca-38d4ef14936b	920bbc7a-cc0e-4893-8aee-581b77842314	bot	### Summary of Backtracking (2 Marks)\n\n- **Backtracking** is an **algorithmic technique** that systematically searches for all possible solutions to a problem by building solutions incrementally, abandoning partial solutions ("backtracking") when they violate problem constraints.\n- It's widely used in solving **constraint satisfaction problems** such as **N-Queens**, **Sum of Subsets**, **Graph Coloring**, **Hamiltonian Cycles**, and **Knapsack Problem**.	2025-06-20 19:32:00.088563+00
cbdd6390-13f7-49df-a1fb-f7a16e27cbe8	920bbc7a-cc0e-4893-8aee-581b77842314	user	Summarize it	2025-06-21 15:12:31.576036+00
77d350ee-ec1a-4a31-9009-e74c98042714	920bbc7a-cc0e-4893-8aee-581b77842314	bot	- **GenPOD** is an **AI-powered print-on-demand (POD) design generator** with features like image creation, editing, and vectorization.\n- The platform now supports **advanced editing tools** (layer-based edits, pose control, object manipulation), and **optimizations** have improved speed and stability.	2025-06-21 15:12:31.576036+00
805feaae-9433-4aa0-825f-4d10b4060264	920bbc7a-cc0e-4893-8aee-581b77842314	user	Summarize it 	2025-06-21 15:13:48.071898+00
38455426-d202-42b4-a969-9d2ff39826e6	0014d802-c8d6-42f3-ba62-743b118f36c1	user	Test	2025-06-21 15:34:56.557566+00
04757b77-648f-4fb9-b0b9-0ca324164f6b	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	- This is a **test** message to check the system response.\n- If you can read this, the **bot is working** correctly.	2025-06-21 15:34:56.557566+00
4931a73d-0a0b-4500-b9fc-51b13ab83faf	0014d802-c8d6-42f3-ba62-743b118f36c1	user	Summarize it	2025-06-21 15:43:13.338169+00
5e42700d-f3ad-43a4-bcb8-5bf60bb3fc42	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	- **GenPOD** is an **AI-powered print-on-demand design generator** with advanced features like **image generation, editing, and vectorization**.\n- The platform now supports **real-time pose editing**, **layer-based editing**, and **flexible object manipulation**, with a stable and intuitive **UI** for users.\n- **Current focus:** Refining **object detection** and further improving the **editor interface**.	2025-06-21 15:43:13.338169+00
b34ff6ab-c9b8-42e5-a416-bbdd065f977c	0014d802-c8d6-42f3-ba62-743b118f36c1	user	can you summarize it again	2025-06-21 15:46:30.625222+00
4fa632ef-115f-4e0f-927a-47f9e90da527	0014d802-c8d6-42f3-ba62-743b118f36c1	user	HI recap 	2025-06-22 13:24:05.167459+00
dcc885b5-4fd4-402c-a386-42b82823034d	0014d802-c8d6-42f3-ba62-743b118f36c1	user	Recap	2025-06-22 15:41:03.36385+00
1e047202-7905-49db-be01-408abcaeec39	920bbc7a-cc0e-4893-8aee-581b77842314	bot	#### Detailed Summary of GenPOD (For 10 Marks)\n\n---\n\n**Introduction to GenPOD**\n\n**GenPOD** is an advanced **AI-powered platform** specifically designed for the **print-on-demand (POD)** market. It leverages artificial intelligence to assist designers, entrepreneurs, and businesses in rapidly generating high-quality designs customized for a variety of POD products such as t-shirts, mugs, phone cases, and more.\n\n---\n\n**Key Features and Capabilities**\n\n1. **AI-Driven Design Creation**:  \n   GenPOD uses sophisticated AI algorithms to automatically create unique images and graphic designs. Users can input prompts or keywords, and the AI will generate corresponding visuals tailored for POD.\n\n2. **Advanced Editing Tools**:  \n   The platform provides a robust set of **editing tools**, including:\n   - **Layer-based editing**: Allows users to manage and modify individual design components without affecting the entire image.\n   - **Pose control and object manipulation**: Lets users adjust the position or orientation of elements in their design.\n   - **Text and color customization**: Provides flexibility in typography and palette to match brand requirements.\n\n3. **Vectorization and Scalability**:  \n   GenPOD can **convert raster images to vector formats**. Vector graphics can be scaled infinitely without loss of quality—a critical requirement for professional POD printing.\n\n4. **Speed and Optimizations**:  \n   Recent updates have enhanced the platform’s speed and stability, enabling faster generation, editing, and export of designs. This makes workflow more efficient and ensures high-quality results.\n\n---\n\n**Practical Example**\n\nImagine a designer wants to launch a new t-shirt collection around the theme “Space Adventure.” Using GenPOD:\n- They input prompts like “astronaut riding a rocket” or “cute alien holding a flag.”\n- The AI generates several design options.\n- The designer fine-tunes the chosen design by adjusting layers (e.g., adding stars, resizing the astronaut, changing colors).\n- They vectorize the final artwork, export it, and upload it straight to their POD marketplace.\n\n---\n\n**Benefits**\n\n- **Time-saving**: Eliminates the need to manually create or search for suitable graphics.\n- **Cost-effective**: Reduces reliance on professional designers.\n- **Customization**: Offers unique, on-brand artwork for niche markets.\n- **Seamless POD integration**: Designs are optimized for direct upload to major POD platforms.\n\n---\n\n**Conclusion**\n\nIn summary, **GenPOD** is revolutionizing the print-on-demand design process by melding **AI creativity**, **advanced editing capabilities**, and **optimized performance**. This enables anyone—even those with minimal graphic design experience—to produce professional-grade, market-ready artwork quickly and efficiently.	2025-06-21 15:13:48.071898+00
04e34415-8007-4b59-9a9e-80cb77825fef	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	**Summary of GenPOD Platform**\n\n---\n\n**Overview**\n\nGenPOD is an advanced **AI-driven print-on-demand design tool** that offers a robust suite of features for creators and businesses in the print-on-demand industry. The platform leverages artificial intelligence to streamline and enhance the design process, focusing on user-friendly operation and powerful customization capabilities.\n\n---\n\n**Key Features and Current Focus**\n\n- **Image Generation and Editing**: GenPOD supports the automatic creation, modification, and enhancement of images using AI for diverse print-on-demand needs.\n- **Vectorization**: The system can convert raster images into **vector graphics**, allowing for scalable, high-quality print designs.\n- **Layer-Based Editing & Object Manipulation**: Users can edit elements individually in a **layered workspace**, performing **real-time pose editing** and **object movement** for greater design flexibility.\n- **Intuitive User Interface (UI)**: Designed for stability and ease-of-use, the platform makes advanced tools accessible, minimizing the steep learning curve typical of graphic design software.\n\n---\n\n**Examples of Functionality**\n\n- **Real-Time Pose Editing**: Instantly adjust the positioning or movement of figures and objects without redrawing the art.\n- **Flexible Object Handling**: Move, resize, or layer design components for unique compositions (e.g., place a new logo on a t-shirt mockup with a single drag-and-drop).\n- **Vectorization Process**: Upload a hand-drawn image; GenPOD converts it to a crisp, scalable vector suitable for large format printing.\n\n---\n\n**Development Focus**\n\nCurrently, GenPOD is **refining object detection algorithms**—improving how the system recognizes and separates different elements within a design. The team is also working to **further enhance the editor interface** for a smoother, more intuitive user experience, ensuring even complex edits are accessible to users at all skill levels.\n\n---\n\n**In Summary**:  \nGenPOD empowers creators by combining **AI-powered image editing**, **vectorization**, and **object segmentation** with an accessible UI—making high-quality, customizable print designs faster and easier than ever before.	2025-06-21 15:46:30.625222+00
65ddaaab-6f20-4810-aae4-06a3d88c049c	920bbc7a-cc0e-4893-8aee-581b77842314	user	What can we conclude	2025-06-21 15:46:53.835458+00
cb355c38-5661-4530-8243-a5f6b19fcd35	920bbc7a-cc0e-4893-8aee-581b77842314	bot	#### Conclusion (2 Marks)\n\n- **GenPOD leverages powerful AI** to automate and simplify the creation of unique, professional-quality print-on-demand designs.\n- It **saves time, reduces costs**, and enables even non-designers to quickly produce and customize scalable artwork for various POD products.	2025-06-21 15:46:53.835458+00
c13e5b62-adcc-4f50-90ab-67f84c83b4c5	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	- **GenPOD** is an **AI-powered print-on-demand design tool** focused on **image generation, editing, and vectorization**.\n- It offers **layer-based editing**, **real-time pose adjustment**, and an **intuitive user interface** for easy and flexible design creation.	2025-06-22 13:24:05.167459+00
cc9a161e-2880-452f-a1ae-f65063e99b03	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	- **GenPOD** is an **AI-powered print-on-demand design platform**.\n- It offers **image generation, vectorization,** and **layer-based editing** with an **intuitive interface** for easy and flexible design creation.	2025-06-22 15:41:03.36385+00
a5d620c0-d4c6-4233-85f2-0f0db22066e1	0014d802-c8d6-42f3-ba62-743b118f36c1	user	Create ,me a flashcard on laws of newton	2025-06-27 18:18:08.60936+00
75a1da80-8771-4ff3-85fa-68cb659c58d3	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	### Flashcard: Newton's Laws of Motion (5 marks)\n\nNewton’s laws of motion are three fundamental principles that form the basis of classical mechanics. **Newton’s First Law** (Law of Inertia) states that an object will remain at rest or move at a constant velocity unless acted upon by an external force. **Newton’s Second Law** explains that the acceleration of an object is proportional to the net force acting on it and inversely proportional to its mass, expressed by the formula: **F = m × a**. **Newton’s Third Law** states that for every action, there is an equal and opposite reaction. These laws explain how forces act on objects to influence their motion and are essential for understanding many physical phenomena.	2025-06-27 18:18:08.60936+00
5db7b3ed-7d8d-4321-a1fe-a43716269a16	0014d802-c8d6-42f3-ba62-743b118f36c1	user	create me flashcards on evolution	2025-06-27 18:19:21.15425+00
84168947-caf8-4c03-b528-1a132e9592e3	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	### Flashcard: Evolution (2 marks)\n\n- **Evolution** is the gradual change in living organisms over time.\n- It occurs mainly through **natural selection** and results in new species formation.\n\n📚 Flashcards have been generated for your prompt!	2025-06-27 18:19:21.15425+00
7cb756ba-f9a2-4b73-875a-c01a783afb8a	0014d802-c8d6-42f3-ba62-743b118f36c1	user	 create me flashcards on evolution	2025-06-27 18:37:01.351657+00
39a262cc-6b04-4175-b15b-b737df69888f	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	### Flashcard: Evolution (2 marks)\n\n- **Evolution** is the gradual change in living organisms over time.\n- Driven mainly by **natural selection**, which favors traits that help survival.\n- Leads to the formation of new **species**.\n\n📚 Flashcards have been generated for your prompt!	2025-06-27 18:37:01.351657+00
944fab08-3ef6-42eb-bdf3-68f784018f9c	0014d802-c8d6-42f3-ba62-743b118f36c1	user	 create me flashcards on India	2025-06-27 18:41:38.33676+00
727c175b-60f5-44fb-aa5c-2aee679d960b	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	### Flashcard: India (2 marks)\n\n- **India** is a country in **South Asia**, known for its vast diversity in culture, language, and geography.\n- The capital city is **New Delhi**.\n- It is the **seventh-largest** country by area and the **second-most populous** in the world.	2025-06-27 18:41:38.33676+00
00e4697e-6a8e-4396-b8bf-ce11064bade6	0014d802-c8d6-42f3-ba62-743b118f36c1	user	 create me flashcards on Indian constitution	2025-06-27 18:43:07.420635+00
6b862452-c294-40f2-b747-2811fe0b9177	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	### Flashcard: Indian Constitution (2 marks)\n\n- The **Indian Constitution** is the **supreme law** of India, adopted on **26 January 1950**.\n- It establishes India as a **sovereign, socialist, secular, democratic republic**.\n- Lays down the framework for the **government**, including the **Fundamental Rights** and **Duties** of citizens.	2025-06-27 18:43:07.420635+00
c38e3c55-e554-4481-9295-25f3dba8cea5	0014d802-c8d6-42f3-ba62-743b118f36c1	user	create me flashcards on Indian constitution	2025-06-27 20:03:32.880053+00
41bbe079-17f3-42d9-a2c9-bd0acc58bacf	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	### Flashcard: Indian Constitution (2 marks)\n\n- The **Indian Constitution** is the **supreme law** of India, adopted on **26 January 1950**.\n- It defines India as a **sovereign, socialist, secular, democratic republic**.\n- Provides for **Fundamental Rights** and **Duties** of citizens, and outlines the structure of the **government**.	2025-06-27 20:03:32.880053+00
f6ff6205-1733-4f70-9c21-1ec24a15105a	0014d802-c8d6-42f3-ba62-743b118f36c1	user	create me flashcards on Indian constitution	2025-06-28 05:18:31.053798+00
46bccd02-1da7-4edd-aabd-b154ef58159e	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	### Flashcards: Indian Constitution (2 marks)\n\n---\n\n**Flashcard 1: Adoption and Significance**  \n- The **Indian Constitution** is the **supreme law** of India, adopted on **26 January 1950**.  \n- It establishes India as a **sovereign, socialist, secular, democratic republic**.\n\n---\n\n**Flashcard 2: Framework and Rights**  \n- The Constitution lays down the **structure of government** and prescribes **Fundamental Rights** and **Duties** for citizens.  \n- It ensures **justice, equality, and liberty** for all.\n\n---\n\n**Flashcard 3: Features**  \n- It is the **longest written constitution** in the world.  \n- It provides for **federal structure** with a **unitary bias**.	2025-06-28 05:18:31.053798+00
0f213899-4fd3-413c-86b1-32780b080fe4	0014d802-c8d6-42f3-ba62-743b118f36c1	user	create me flashcards on G7 summit	2025-06-28 05:27:13.489125+00
c2f3499a-d605-42d2-8336-3a640c84ca4f	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	### Flashcards: G7 Summit (2 Marks)\n\n---\n\n**Flashcard 1: What is G7?**  \n- The **G7 (Group of Seven)** is an informal forum of the world's **seven major advanced economies**: USA, UK, France, Germany, Italy, Canada, and Japan.\n- It discusses **global economic issues**, security, and other urgent world matters.\n\n---\n\n**Flashcard 2: Purpose and Meetings**  \n- The **G7 Summit** is held **annually** and allows leaders to **coordinate policies** and address **challenges** like climate change and pandemics.\n- The summit has **no legal binding decisions**, but shapes international priorities.\n\n---\n\n**Flashcard 3: Importance**  \n- The group influences **global governance** and represents **over 40% of global GDP**.\n- It provides a platform for **policy cooperation** among powerful democracies.	2025-06-28 05:27:13.489125+00
17322050-5897-4ff6-b3d9-a99346fb71af	0014d802-c8d6-42f3-ba62-743b118f36c1	user	create me notes on G7 summit	2025-06-28 08:38:59.427633+00
1e50306b-3293-49bf-9e3e-558500ad1884	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	### G7 Summit (2 Marks Notes)\n\n- The **G7 Summit** is an annual meeting of leaders from the **Group of Seven** countries: **USA, UK, France, Germany, Italy, Canada, and Japan**.\n- It discusses **global economic issues**, international security, and challenges like **climate change**.\n- Though decisions are not legally binding, the G7 shapes **international policies** and represents **major advanced economies**.	2025-06-28 08:38:59.427633+00
51a95f7a-0fef-46cf-aff0-0ad1423f9339	0014d802-c8d6-42f3-ba62-743b118f36c1	user	Can you summarize the assignment.	2025-08-03 08:23:39.618494+00
af41eee6-7633-49df-b72a-20d5eae30b0a	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	- The assignment covers real-world **NLP applications** (like chatbots, sentiment analysis, and machine translation), **techniques used** (such as speech recognition, intent recognition, tokenization, encoder-decoder models), and compares **stemming vs lemmatization**.\n- It asks about **challenges in morphological parsing** for languages with rich inflection, and how they can be addressed using techniques like state machines, machine learning, and neural models.\n- The assignment also discusses **topic segmentation methods** (TextTiling vs machine learning), and explores **syntactic ambiguity** in sentences and how NLP systems can resolve them using parsing and context.	2025-08-03 08:23:39.618494+00
7fee81bb-2215-4ba5-99af-14728d13ebf2	0014d802-c8d6-42f3-ba62-743b118f36c1	user	Hello	2025-08-03 08:26:59.537483+00
912db141-54d0-43ba-b8a7-a0b7da30a424	0014d802-c8d6-42f3-ba62-743b118f36c1	bot	- **Hello!** How can I help you today?\n- If you have any questions or need help with your assignment, feel free to ask!	2025-08-03 08:26:59.537483+00
950f3745-3a25-453f-b60b-6982df9c55b0	920bbc7a-cc0e-4893-8aee-581b77842314	user	Give me the insights in a tabular format	2025-08-03 09:04:29.424491+00
29565ee3-4c31-4b77-8a25-8ec04bdca8f6	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	How does physical Layer work	2025-10-07 14:50:32.927603+00
0f979418-ce86-44f5-ba3c-6b8aa6945ee5	920bbc7a-cc0e-4893-8aee-581b77842314	bot	| **Aspect**                | **Insight**                                                                                                    |\n|---------------------------|----------------------------------------------------------------------------------------------------------------|\n| **AI-Driven Design**      | **GenPOD** uses advanced AI to auto-generate unique, high-quality **POD designs** from user prompts or keywords.|\n| **Editing & Customization** | Offers **layer editing, vectorization, text & color tools** for customization—making design fast and flexible.  |\n| **Efficiency & Benefits** | **Saves time and cost**, enabling even non-designers to create market-ready, scalable artwork for POD products. |\n	2025-08-03 09:04:29.424491+00
42c47045-14a2-4bc4-869b-71364a0b2fa1	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	OSI Model Layers	2025-08-10 14:52:05.107902+00
8fe8ac81-e687-4ca7-b7fc-40e246963728	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	## OSI Model Layers (10 Marks)\n\nThe **OSI Model** (Open Systems Interconnection Model) is a conceptual framework used to understand and implement network communications between computers. It divides the communication process into **seven distinct layers**, each with specific functions and protocols. Below is a detailed explanation of each layer:\n\n---\n\n### 1. Physical Layer\n- **Function:** Deals with the physical connection and transmission of raw bit streams over a physical medium (`cables`, `hubs`, `repeaters`).\n- **Key Role:** Defines **electrical signals**, **cable types**, **connector types**, and **transmission rates**.\n- _Example:_ Ethernet cables, fiber optics.\n\n### 2. Data Link Layer\n- **Function:** Establishes and maintains reliable **links** between nodes on the same network segment. Responsible for **error detection/correction** and **framing**.\n- **Protocols:** `Ethernet`, `PPP`, `HDLC`.\n- _Example:_ MAC addresses are used for hardware addressing.\n\n### 3. Network Layer\n- **Function:** Provides logical addressing and routing of packets across different networks. Enables **internetworking**.\n- **Protocols:** `IP` (Internet Protocol), `ICMP`, `IPsec`.\n- _Example:_ Routers operate at this layer to forward packets.\n\n### 4. Transport Layer\n- **Function:** Ensures reliable data transmission between end systems. Responsible for **segmentation**, **flow control**, **error recovery**, and **connection management**.\n- **Protocols:** `TCP` (Transmission Control Protocol), `UDP` (User Datagram Protocol).\n- _Example:_ TCP guarantees delivery, ordering, and error checking.\n\n### 5. Session Layer\n- **Function:** Manages and controls the **dialogue** between two computers. Establishes, maintains, and terminates **sessions**.\n- **Protocols:** `NetBIOS`, `RPC` (Remote Procedure Call).\n- _Example:_ Managing persistent login sessions in web services.\n\n### 6. Presentation Layer\n- **Function:** Translates, encrypts, and compresses data. Ensures data is presented in a readable format for the application layer.\n- **Process:** Data encoding, character set translation, **encryption/decryption**.\n- _Example:_ SSL encryption for secure web browsing, JPEG/PNG conversion.\n\n### 7. Application Layer\n- **Function:** Provides network services to end-user applications. It is closest to the user and interacts directly with software like browsers or email clients.\n- **Protocols:** `HTTP`, `FTP`, `SMTP`, `DNS`.\n- _Example:_ Browsing websites, sending emails.\n\n---\n\n### Diagram (Descriptive)\n\n```\n+------------------+      <-- Layer 7: Application\n|    Application   |      <-- Layer 6: Presentation\n|   Presentation   |      <-- Layer 5: Session\n|      Session     |      <-- Layer 4: Transport\n|     Transport    |      <-- Layer 3: Network\n|     Network      |      <-- Layer 2: Data Link\n|     Data Link    |      <-- Layer 1: Physical\n|    Physical      |\n+------------------+\n```\n_Data moves from Application to Physical as it is sent, and from Physical to Application as it is received._\n\n---\n\n## Summary Table\n\n| Layer | Function                          | Example Protocols   | Devices         |\n|-------|-----------------------------------|---------------------|-----------------|\n| 7     | Application (User services)       | HTTP, FTP           | Browser, Email  |\n| 6     | Presentation (Data format)        | SSL, JPEG           | Converter, Encryptor |\n| 5     | Session (Dialog control)          | RPC, NetBIOS        | Session Manager |\n| 4     | Transport (Reliability, Flow)     | TCP, UDP            | Firewall        |\n| 3     | Network (Routing, Addressing)     | IP, ICMP            | Router          |\n| 2     | Data Link (Frames, Error check)   | Ethernet, PPP       | Switch, Bridge  |\n| 1     | Physical (Hardware transmission)  | Ethernet, Fiber     | Hub, Cable      |\n\n---\n\n### Final Notes\n\nThe **OSI Model** is essential for understanding how data travels through a network—from the user's application down to the physical transmission medium. It encourages standardization, interoperability, and troubleshooting by dividing network functions into logical layers, each managed by dedicated protocols and devices.	2025-08-10 14:52:05.107902+00
aaf9faf7-36d4-487d-87ba-1849a91d35c0	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	user	hi\n	2025-08-20 06:29:30.261569+00
a34a5afe-e616-4992-8716-2d8de0aea1fd	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	bot	- **Hello!** How can I assist you today?\n- If you have any **questions** or need **help**, feel free to ask!	2025-08-20 06:29:30.261569+00
51b3097e-a9d2-4899-b009-d7020526bae7	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	user	Hi	2025-09-10 14:48:28.458007+00
b5d158d4-504f-479d-9834-dbcc155faf8f	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	bot	Hello! How can I help you today?  \nIf you have a question or need assistance, just let me know.  \nI’m here to assist with any queries you might have.	2025-09-10 14:48:28.458007+00
1a83a9bc-1323-40e7-ba0b-97aba8f4663c	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	user	hi	2025-09-20 06:21:10.979404+00
dd945921-d607-486c-857f-9eeb25076c73	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	bot	Hello! How can I help you today?  \nIf you have a question or need information, just let me know.  \nI'm here to assist you with anything you need.	2025-09-20 06:21:10.979404+00
698a7cd3-ecf1-4415-91e0-c3c1b3e1d809	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	user	Hello	2025-09-23 15:11:03.319996+00
13037a97-1cd0-46fb-86a2-cf8eeeeae43c	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	bot	Hello! How can I help you today?  \nLet me know if you have any questions or need information.  \nI’m here to assist you with whatever you need.	2025-09-23 15:11:03.319996+00
c584fa50-e564-4259-a154-f111daa73b7f	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	user	I am testing the pricing\n	2025-09-23 15:13:16.779316+00
0be7abee-12f5-46fb-93f3-49a06de95e9e	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	bot	You are checking how pricing works, likely to understand costs or structures for services or products. Pricing tests help confirm accuracy, transparency, and ensure the expected rates are applied. It's essential for budgeting and planning purposes.	2025-09-23 15:13:16.779316+00
7c4fb491-5797-4a21-aace-8d576c3fc047	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	user	Nah I applied the backend and testing that\n	2025-09-23 15:13:47.710118+00
204c7f31-b525-4ee0-a829-46228e098a94	fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	bot	You’ve applied backend changes and are now testing to ensure everything works as expected. This involves validating server logic, integration points, and checking APIs or data flow. It’s a crucial step to confirm reliability and catch any bugs before deployment.	2025-09-23 15:13:47.710118+00
06590895-cedb-4f40-bc9a-09e9485298f9	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	When was this model invented?\n	2025-10-07 10:17:14.500616+00
532987fe-6d53-4278-959d-844ea7f414eb	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	The OSI Model was invented in the late 1970s by the International Organization for Standardization (ISO). Its first standard was published in 1984 to promote interoperability and standardize networking communication worldwide.	2025-10-07 10:17:14.500616+00
4caba8fb-f39e-412b-b53e-435b1ba67b33	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	What was the other main reference model invented after this?	2025-10-07 10:18:20.149112+00
b5305c22-758d-4d92-a826-1e472cbe98dc	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	The other main reference model invented after the OSI Model is the **TCP/IP Model** (also called the Internet Protocol Suite). Developed by the U.S. Department of Defense in the 1970s, it became the foundation for the modern Internet and is widely used for practical networking today. The TCP/IP model has four layers and is simpler compared to OSI.	2025-10-07 10:18:20.149112+00
3c12abf4-3621-4dcb-b0fc-2481b034bf66	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	Give a very brief explanation on it	2025-10-07 10:18:58.654673+00
31232cba-4853-4fc2-8231-fa0341dce408	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	The TCP/IP model is a networking framework that defines how data is transmitted over the Internet. It consists of four layers: Application, Transport, Internet, and Network Access. It standardizes communication protocols, enabling devices to connect and exchange information efficiently across networks.	2025-10-07 10:18:58.654673+00
31e7eb13-bc5d-441a-b5f5-f29ab0c30c92	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	Explain it in detail	2025-10-07 10:19:16.006741+00
d1306b41-bbba-403c-a0f2-99c0e17e07d1	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	### Definition:\nThe TCP/IP Model (Transmission Control Protocol/Internet Protocol Model) is a standardized networking framework that describes how data is transmitted and exchanged over interconnected networks, such as the Internet. It consists of four abstraction layers that enable communication between devices.\n\n### Explanation:\nThe TCP/IP model was developed in the 1970s to provide a practical, robust protocol suite for networking and has become the foundation of the Internet. Its four layers are:  \n1. **Application Layer:** Handles high-level protocols and user interfaces (e.g., HTTP, FTP, SMTP).\n2. **Transport Layer:** Manages end-to-end communication, error correction, and flow control (mainly TCP and UDP).\n3. **Internet Layer:** Deals with logical addressing, routing, and delivering packets across networks using IP.\n4. **Network Access Layer:** Responsible for the physical transmission of data over network media, including hardware addressing and protocols.\n\nEach layer performs specific functions and interacts with the layers directly above and below. Together, the layers help break down complex networking tasks, facilitate interoperability between hardware and software, and ensure reliable, efficient data communication across diverse systems.\n\n### Examples:\n- **Sending an Email:** When you send an email, your computer uses the TCP/IP model—data travels from your email client (application layer), is packaged by TCP (transport layer), routed using IP (internet layer), and transmitted physically through Wi-Fi or Ethernet (network access layer).\n- **Browsing a Website:** When accessing a website, HTTP uses the TCP/IP stack to transmit web page data reliably from the server to your browser.	2025-10-07 10:19:16.006741+00
0155ab66-583c-405d-a557-417a86a62dea	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	What are main functions of Session layer	2025-10-07 14:04:43.330348+00
77a6b58b-5d0f-40be-ab42-0070271b2b54	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	### Definition:\nThe Session layer is the fifth layer in the OSI Model. Its main function is to manage and control the dialog (sessions) between two computers, establishing, maintaining, and terminating connections. It ensures that data exchange happens in a synchronized and organized manner.\n\n### Explanation:\nThe Session layer is responsible for setting up, coordinating, and concluding communication sessions between applications running on networked devices. This layer controls dialogues, meaning it determines whether communication is half-duplex, full-duplex, or simplex. It provides mechanisms for opening, closing, and managing sessions, making sure that data exchange between applications is orderly and can recover in case of interruptions. Session layer protocols can synchronize data flow by inserting checkpoints in long transmissions, so if the connection is broken, only the data from the last checkpoint needs to be resent, ensuring efficiency and reliability. Common functions include establishing session parameters, authentication, managing session tokens, and recovering lost sessions, allowing users to resume interrupted activities without starting over.\n\n### Examples:\n- In a video conference call, the session layer manages the ongoing connection so participants can communicate smoothly, handling start, join, and end procedures.\n- When logging into a remote system, the session layer helps authenticate your session and maintain your state until you log out.	2025-10-07 14:04:43.330348+00
f468c366-7fbb-4e09-9054-308340029aeb	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	### Definition:\nThe Physical Layer is the lowest layer of the OSI model. It is responsible for the actual transmission and reception of raw data bits over a physical medium, such as cables or wireless signals.\n\n### Explanation:\nThe Physical Layer defines the hardware and means of sending data over network connections. Its main function is to convert binary data (0s and 1s) from higher layers into signals (electrical, optical, or radio) to be transmitted through the network media like copper wires, fiber optics, or air. It deals with specifications for cables, connectors, electrical voltages, frequencies, and data transmission rates. The physical layer doesn’t concern itself with what the data means—instead, it ensures how the data physically moves from one device to another. Key tasks include signal encoding, bit synchronization, managing transmission modes (simplex/duplex), and detecting physical errors (like signal loss). Overall, it acts as the foundation for all network communication, ensuring data can be sent and received as raw bits across network hardware.\n\n### Examples:\n- Ethernet cables and Wi-Fi radio signals transmitting data between computers and routers.\n- Conversion of digital data to electrical pulses sent across a copper wire in a traditional LAN setup.	2025-10-07 14:50:32.927603+00
7bbda1ae-43b0-49e9-a04b-2f7120ec8ddc	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	And also tell me the protocols in Data Link layer\n	2025-10-07 14:54:52.305319+00
77f35d9f-def6-4617-8f11-1ed75b628203	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	### Definition:\nThe Data Link layer is the second layer of the OSI model and is responsible for reliable data transfer, error detection, and framing between connected devices over a physical network.\n\n### Explanation:\nThe Data Link layer acts as an intermediary between the Physical layer and the Network layer. Its main role is to ensure error-free and orderly data transmission over the physical links. It breaks data from the Network layer into frames, adds necessary headers and trailers for addressing and error checking, and manages how devices on the same network medium share access.  \nMajor protocols at this layer include **Ethernet (IEEE 802.3)**—used widely in LANs for framing and CSMA/CD media access control, **Point-to-Point Protocol (PPP)**—for direct communication between two nodes, and **High-Level Data Link Control (HDLC)**—used in WAN links for reliable and synchronized frame transfer. Other notable protocols are **Frame Relay** (for WANs) and **MAC (Media Access Control)** sublayer protocols for device addressing within networks. These protocols handle error detection (e.g., CRC) and flow control to prevent data loss or duplication.\n\n### Examples:\n- **Ethernet (IEEE 802.3)** in wired LANs handles how data frames are sent and received between computers and switches.\n- **PPP** protocol managing direct internet connections, such as over phone lines or dedicated circuits.	2025-10-07 14:54:52.305319+00
ecb73258-ee2b-490e-8a6e-fb55e009ceac	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	What are the elementary protocols?	2025-10-07 14:56:22.421735+00
c48c3e5b-46b5-4d2e-a31e-e7421eb433f6	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	### Definition:\nElementary protocols are basic communication rules or procedures used to control and manage data exchange between two network entities, defining simple interactions like frame transfer, acknowledgements, or error handling.\n\n### Explanation:\nElementary protocols form the foundation for reliable data communication in computer networks. They specify straightforward mechanisms for sending and receiving data frames over a link and outline how parties should react to successes or failures in transmission. Common examples include the **Stop-and-Wait protocol**, where the sender transmits one frame and waits for an acknowledgement before sending the next, and the **Automatic Repeat reQuest (ARQ)** methods, which ensure that lost or corrupted frames are retried. These protocols focus on simple tasks such as flow control, error detection and correction, and maintaining data integrity during transmission. Their design makes them easy to implement and essential for teaching more complex protocol structures in networking courses. Although limited in efficiency for high-speed networks, elementary protocols are critical for understanding basic network communication principles and building more advanced protocols.\n\n### Examples:\n- **Stop-and-Wait ARQ**: The sender transmits one frame and waits for an acknowledgement before sending the next frame.\n- **Go-Back-N ARQ**: The sender can transmit several frames before needing an acknowledgement, but must resend all frames from a lost one onwards if an error is detected.	2025-10-07 14:56:22.421735+00
8e2e25ba-2036-4f58-bd4c-7743fae0f4ac	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	Explain both in  detail	2025-10-07 15:00:21.058424+00
c5e98d23-21fb-4c9e-abb4-1e6d2a0e5e87	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	## Data Link Layer and Elementary Protocols (Detailed 10-mark Answer)\n\n### Definition:\nThe **Data Link layer** is the second layer of the OSI model, responsible for reliable data transfer, error detection, framing, and access control over a physical network link.  \n**Elementary protocols** are basic rules and procedures designed for managing fundamental data communication tasks, such as simple frame transfer, acknowledgments, and error handling between two network endpoints.  \nThese protocols form the foundation of reliable data exchange and serve as building blocks for more advanced networking procedures.\n\n### Example:\nConsider the **Stop-and-Wait ARQ protocol** at the Data Link layer: A sender transmits one frame, waits for the receiver's acknowledgment, and retransmits the frame if an error or timeout occurs. This demonstrates both error detection and flow control, using basic rules for reliable communication between devices.\n\n### Detailed Answer:\nThe **Data Link layer** operates directly above the Physical layer, managing how raw bits are packaged into frames and reliably transmitted between adjacent network nodes. It handles critical functions such as framing, which structures the data with headers and trailers for identification and error checking; addressing, which uses MAC addresses for unique device identification; and error detection using methods like cyclic redundancy checks (CRC). This layer also controls how multiple devices access the network medium using protocols like CSMA/CD in Ethernet, preventing collisions and ensuring orderly sharing of bandwidth. Additionally, it provides flow control mechanisms to prevent fast senders from overwhelming slow receivers and includes recovery techniques for lost or corrupted frames.\n\n**Elementary protocols** are simple, foundational protocols that facilitate core communication tasks—essentially representing the minimum structure needed for reliable data transfer. They typically manage transmission one frame at a time, ensure receipt through acknowledgements, and handle errors with minimal retransmission logic. The Stop-and-Wait protocol, for example, enforces that the sender transmits a single frame and waits for a correct acknowledgment before proceeding—thus guaranteeing order and integrity. The Go-Back-N and Selective Repeat ARQ methods introduce more sophisticated error recovery but remain fundamentally simple, focusing only on successful frame delivery and basic error handling.\n\nTogether, the Data Link layer and elementary protocols ensure that packets are correctly framed, transmitted, and received between directly connected devices. Their clear separation of functions allows higher layers to focus on routing, sessions, and application logic, while the Data Link layer guarantees the network’s operational dependability—making these concepts vital in both theory and practice for network engineers and computer scientists.	2025-10-07 15:00:21.058424+00
f455b4cc-3af8-477a-a280-4bd4140a81f5	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	Summarize this chat	2025-10-07 15:09:14.683872+00
1eb13dec-2a61-4581-b4f6-657ccbcf2807	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	### Definition:\nThis chat explored the Data Link layer of the OSI model and elementary protocols used for reliable network communication. Elementary protocols are basic sets of rules governing simple frame transfer, acknowledgements, and error handling between network devices. They provide the core mechanisms for dependable data transmission over a direct network link.\n\n### Example:\nFor instance, the Stop-and-Wait ARQ protocol allows the sender to transmit one frame at a time and requires an acknowledgement before the sender can continue, ensuring both flow control and error recovery on the data link.\n\n### Detailed Answer:\nThe Data Link layer, positioned above the Physical layer in the OSI model, is tasked with organizing raw data bits into frames and ensuring their reliable transfer between adjacent network nodes. It achieves this by adding headers and trailers for error detection, framing, and addressing (usually through MAC addresses). The layer implements mechanisms such as cyclic redundancy check (CRC) for error detection, flow control to balance sender and receiver speeds, and access control to prevent data collisions on shared media (e.g., using CSMA/CD in Ethernet networks).\n\nElementary protocols are simple yet essential in managing how data is exchanged and acknowledged at the Data Link layer. These include protocols like Stop-and-Wait ARQ, where a sender transmits a single frame, waits for an acknowledgement, and retransmits if necessary due to errors or timeouts. This structure guarantees ordered and reliable delivery at the cost of efficiency. More advanced protocols such as Go-Back-N ARQ and Selective Repeat ARQ expand this logic to allow windowed transmissions and more nuanced error recovery, but remain centered on robust, elementary rules. Overall, understanding these protocols and their Data Link layer context is crucial for appreciating how reliable communication is established in computer networks, laying the foundation for higher-level networking and application services.	2025-10-07 15:09:14.683872+00
fec8f60b-2981-4e0f-9c36-5756864e7343	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	user	Hello	2025-10-07 17:43:03.843338+00
851780c6-f156-4412-bb6f-f9cb233cb40a	18d74a7c-2fd9-4b52-96d4-609e176e2ee7	bot	Hello! How can I help you today? If you have a specific topic or question you’d like answered (for 2, 5, or 10 marks), please let me know. You can ask about computer networks, protocol layers, or any other subject of interest!	2025-10-07 17:43:03.843338+00
74858b97-601b-4547-9124-a82a4f21871f	25b264ec-318a-445e-ba66-bd9d40c9bb02	user	hi\n	2025-10-08 13:50:38.247653+00
a333e851-70df-4111-a56c-98ec76cf1fc5	25b264ec-318a-445e-ba66-bd9d40c9bb02	bot	Hello! How can I help you today? Please let me know if you have any questions or need assistance with a topic.	2025-10-08 13:50:38.247653+00
\.


--
-- Data for Name: notes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notes (id, user_id, session_id, content, source_type, created_at) FROM stdin;
082d047b-6264-41ef-a88b-823b88669a2a	d0bb82c6-fff5-454e-a590-d83900072364	5df0acb9-8c44-4f53-a4c3-0738775e8b96	### 1. Real-world Applications of NLP\n\n**i) Chatbots and Virtual Assistants**\n- Use **NLP** to interpret and generate human-like responses in real-time conversations.\n- Key techniques:\n  - **Speech Recognition (ASR):** Converts spoken input to text.\n  - **Intent Recognition:** Classifies user’s goal (e.g., using sequence models).\n  - **Named Entity Recognition (NER):** Extracts important entities like dates, names, locations.\n  - **Dialog Management:** Maintains context across conversation turns (uses state machines or transformer models).\n\n**ii) Sentiment Analysis**\n- Determines if a text expresses **positive, negative, or neutral** sentiment.\n- Techniques:\n  - **Text Preprocessing:** Tokenization, stop-word removal, stemming/lemmatization.\n  - **Feature Extraction:** Converts text to numerical form (e.g., TF-IDF, word embeddings).\n  - **Classification Models:** Machine learning (Naive Bayes) or deep learning (LSTM, BERT) for sentiment prediction.\n\n**iii) Machine Translation**\n- Automatically translates text between languages (e.g., **English↔Hindi**).\n- Techniques:\n  - **Tokenization & Language Detection:** Segments text, identifies source language.\n  - **Encoder-Decoder Architecture:** Encodes source, decodes into target.\n  - **Post-processing:** Adjusts grammar, punctuation for fluency.\n\n---\n\n### 2. Stemming vs. Lemmatization\n\n| Stemming                              | Lemmatization                              |\n|----------------------------------------|--------------------------------------------|\n| Chops off word endings (e.g., “studies” → “studi”)        | Reduces words to dictionary form (lemma) (e.g., “studies” → “study”)    |\n| May produce non-words                  | Always returns valid words                 |\n| Fast, simple, less accurate            | Slower, more accurate                      |\n| Use when speed > accuracy (e.g., spam detection) | Use when context/accuracy matters (e.g., legal docs)      |\n\n**Example:**\n- Stemming: “better” → “bet”, “playing” → “play”\n- Lemmatization: “better” → “good”, “playing” → “play”\n\n---\n\n### 3. Challenges in Morphological Parsing of Highly Inflected Languages\n\n- **Data Sparsity:** Many word forms for a single root due to inflections (e.g., Turkish).\n- **Ambiguity:** One surface form may map to multiple base forms/meanings.\n- **Non-concatenative Morphology:** Morphemes inserted within root (e.g., Arabic), not just appended.\n- **Compound Words & Orthographic Changes:** Words joined together, spelling changes on adding suffixes (e.g., “studies” vs “study”).\n  \n**Solutions:**\n- **Finite-State Morphological Analyzers:** Use state machines to model root+affixes.\n- **Statistical/ML Methods:** Train on annotated corpora for predicting root/morphemes.\n- **Neural Approaches:** Use models like LSTMs or Transformers for morphological segmentation.\n- **Contextual Analysis:** Use POS tagging and sentence context to resolve ambiguity.\n\n---\n\n### 4. Topic Segmentation: TextTiling vs. Machine Learning-based Methods\n\n| Method                  | Strengths                                              | Weaknesses                                           | Precision | Recall | F1-Score |\n|-------------------------|-------------------------------------------------------|------------------------------------------------------|-----------|--------|----------|\n| **TextTiling**          | Simple, interpretable, no labeled data needed         | Fails with gradual topic change, noisy/short data    | ~0.65     | ~0.60  | ~0.61    |\n| **ML-based**            | High accuracy, domain adaptable                       | Needs labeled data, may overfit                      | ~0.85     | ~0.80  | ~0.82    |\n\n**Takeaway:** ML-based methods outperform TextTiling but need more data/resources.\n\n---\n\n### 5. Syntactic Ambiguity Example\n\n**Ambiguous sentence:** *“I saw the boy on the beach with my binoculars.”*\n\n**Interpretations:**\n1. The **observer** used binoculars to see the boy.\n2. The **boy** had the binoculars.\n\n**NLP Disambiguation Approaches:**\n- **Syntactic Parsing:** Parse trees to reveal sentence structure.\n- **Contextual Clues:** Surrounding sentences clarify reference (e.g., mention of “I focused…” helps assign “my binoculars” to the observer).\n- **Pre-trained Language Models:** Use BERT/GPT to infer the most probable interpretation from context.\n- **Coreference Resolution:** Determines ownership or relation of “my binoculars” to other entities.\n---	file	2025-08-07 15:04:59.267654+00
\.


--
-- Data for Name: plans; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.plans (id, name, description, price, message_limit, is_active, notes_limit, flashcards_limit, billing_cycle) FROM stdin;
1	Free	Basic free tier with limited access	0	20	t	5	5	lifetime
2	Pro - Monthly	Affordable plan with higher daily limits	399	40	t	100	100	monthly
3	Pro - Yearly	Affordable yearly plan with higher daily limits	3999	40	t	100	100	yearly
4	Premium - Monthly	Unlimited access to everything	799	\N	t	\N	\N	monthly
5	Premium - Yearly	Unlimited yearly access to everything	7999	\N	t	\N	\N	yearly
\.


--
-- Data for Name: quiz_attempts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quiz_attempts (id, user_id, session_id, question_id, user_answer, verdict, explanation, score, created_at, attempt_number) FROM stdin;
1edae04a-5168-4b4f-94ae-de8989025ec8	d0bb82c6-fff5-454e-a590-d83900072364	a5b47f69-5d1a-4677-adc0-364476b001d5	596027d2-d8b5-47eb-afd8-5d5cc1e3c84f	Physical layer transmits the data from one host to other.	Incorrect	The answer mentions transmission of data between hosts, which is part of the Physical Layer's role, but it does not specify that it is responsible for the transmission of raw bit streams over a physical medium or the physical connection itself.  \nCorrect Answer: The Physical Layer deals with the physical connection and transmission of raw bit streams over a physical medium.	0	2025-10-06 14:52:46.51252+00	1
93888d98-1d3f-4407-831c-740d44cd004c	d0bb82c6-fff5-454e-a590-d83900072364	a5b47f69-5d1a-4677-adc0-364476b001d5	32927925-270d-4048-9160-dcd5ee377134	TCP and UDP	Incorrect	TCP and UDP are transport layer protocols, not data link layer protocols. The correct protocols for the data link layer are Ethernet and PPP.  \nCorrect Answer: Ethernet and PPP are two protocols used at the Data Link Layer.	0	2025-10-06 14:52:46.51252+00	1
\.


--
-- Data for Name: quizzes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.quizzes (id, session_id, user_id, question, correct_answer, options, created_at, type, correct_option) FROM stdin;
596027d2-d8b5-47eb-afd8-5d5cc1e3c84f	a5b47f69-5d1a-4677-adc0-364476b001d5	d0bb82c6-fff5-454e-a590-d83900072364	What is the main function of the Physical Layer in the OSI Model?	The Physical Layer deals with the physical connection and transmission of raw bit streams over a physical medium.	\N	2025-10-06 14:51:33.424892+00	short	\N
32927925-270d-4048-9160-dcd5ee377134	a5b47f69-5d1a-4677-adc0-364476b001d5	d0bb82c6-fff5-454e-a590-d83900072364	Name two protocols used at the Data Link Layer of the OSI Model.	Ethernet and PPP are two protocols used at the Data Link Layer.	\N	2025-10-06 14:51:33.424892+00	short	\N
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sessions (id, user_id, created_at, title) FROM stdin;
920bbc7a-cc0e-4893-8aee-581b77842314	d0bb82c6-fff5-454e-a590-d83900072364	2025-06-17 15:00:53.88395+00	Hello test
0014d802-c8d6-42f3-ba62-743b118f36c1	d0bb82c6-fff5-454e-a590-d83900072364	2025-06-21 15:34:38.304932+00	Test1
18d74a7c-2fd9-4b52-96d4-609e176e2ee7	d0bb82c6-fff5-454e-a590-d83900072364	2025-08-10 14:51:49.732364+00	Computer Networks
fd28d559-a41c-4f57-8f49-3ec78f5bdcb6	d0bb82c6-fff5-454e-a590-d83900072364	2025-08-20 06:29:15.698825+00	Test chat
2a07b596-819a-4366-a9d0-0a0431f8179f	73acf1c7-9683-47dc-ba10-1a6361c66f0d	2025-09-10 14:42:47.436589+00	Testing
25b264ec-318a-445e-ba66-bd9d40c9bb02	d0bb82c6-fff5-454e-a590-d83900072364	2025-10-08 13:50:32.418825+00	test
\.


--
-- Data for Name: studysessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.studysessions (id, user_id, title, file_name, created_at, file_type) FROM stdin;
aebfe132-a9e4-4344-bc9f-95cd75a52327	d0bb82c6-fff5-454e-a590-d83900072364	create me flashcards on Indian constitut...	chat	2025-06-27 20:03:32.912044+00	flashcards
9e3f36fc-f15e-4c35-a279-df0c9408f658	d0bb82c6-fff5-454e-a590-d83900072364	create me flashcards on Indian constitut...	chat	2025-06-28 05:18:31.08796+00	flashcards
f276ebaa-f020-4124-a20e-b1662b99a3d5	d0bb82c6-fff5-454e-a590-d83900072364	create me flashcards on G7 summit	chat	2025-06-28 05:27:13.522642+00	flashcard
164ef914-246e-4c5d-9d38-cbee31a3a8a2	d0bb82c6-fff5-454e-a590-d83900072364	Hello World	GenPOD_Progress_Summary.pdf	2025-08-07 13:22:32.793879+00	flashcard
5df0acb9-8c44-4f53-a4c3-0738775e8b96	d0bb82c6-fff5-454e-a590-d83900072364	cancel test	NLP_Assignment-1.pdf	2025-08-07 15:04:44.59652+00	notes
915ada3a-2603-49df-a661-28b67085faf2	d0bb82c6-fff5-454e-a590-d83900072364	NLP test flashcards	LECT-NLP-0.pdf	2025-08-20 06:47:02.374737+00	flashcard
a5b47f69-5d1a-4677-adc0-364476b001d5	d0bb82c6-fff5-454e-a590-d83900072364	CN Quiz	from_chat	2025-10-06 14:51:29.143285+00	quiz
\.


--
-- Data for Name: usage_limits; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usage_limits (id, user_id, date, messages_used, notes_used, flashcards_used) FROM stdin;
1	d0bb82c6-fff5-454e-a590-d83900072364	2025-10-07	11	0	0
\.


--
-- Data for Name: user_subscriptions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_subscriptions (id, user_id, plan_id, start_date, end_date, is_active, razorpay_order_id, razorpay_payment_id, subscription_type) FROM stdin;
2	73acf1c7-9683-47dc-ba10-1a6361c66f0d	1	2025-09-23 15:09:05.444753	\N	t	\N	\N	monthly
3	1aebeeac-97d9-41e9-a95c-ff51fdb4d343	1	2025-09-23 15:09:05.446219	\N	t	\N	\N	monthly
1	d0bb82c6-fff5-454e-a590-d83900072364	2	2025-10-09 09:26:39.531101	2025-11-08 09:26:39.531101	t	order_RRK8Fb9JWMYthh	pay_RRKAeAICa5nAb2	monthly
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, email, hashed_password, plan, created_at) FROM stdin;
73acf1c7-9683-47dc-ba10-1a6361c66f0d	Niccunj	niccunjbajaj@gmail.com	$2b$12$POkpfJCRA.NSVYZptyfFPeAuJJWp5QJfn7n2pBG4eVVMa7esi0JxG	free	2025-06-12 08:03:45.597423+00
1aebeeac-97d9-41e9-a95c-ff51fdb4d343	Niccunj Bajaj	niccunjbajaj2006@gmail.com	\N	free	2025-06-12 09:08:38.630192+00
d0bb82c6-fff5-454e-a590-d83900072364	Niccunj BAJAJ	nikkunjbajaj25@gmail.com	\N	Pro - Monthly	2025-06-12 08:01:13.0698+00
\.


--
-- Name: plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.plans_id_seq', 5, true);


--
-- Name: usage_limits_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usage_limits_id_seq', 1, true);


--
-- Name: user_subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.user_subscriptions_id_seq', 3, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: flashcards flashcards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.flashcards
    ADD CONSTRAINT flashcards_pkey PRIMARY KEY (id);


--
-- Name: long_term_memory long_term_memory_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.long_term_memory
    ADD CONSTRAINT long_term_memory_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (id);


--
-- Name: plans plans_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plans
    ADD CONSTRAINT plans_name_key UNIQUE (name);


--
-- Name: plans plans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plans
    ADD CONSTRAINT plans_pkey PRIMARY KEY (id);


--
-- Name: quiz_attempts quiz_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_pkey PRIMARY KEY (id);


--
-- Name: quizzes quizzes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quizzes
    ADD CONSTRAINT quizzes_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: studysessions studysessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.studysessions
    ADD CONSTRAINT studysessions_pkey PRIMARY KEY (id);


--
-- Name: usage_limits unique_user_date; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_limits
    ADD CONSTRAINT unique_user_date UNIQUE (user_id, date);


--
-- Name: quiz_attempts uq_user_question_attempt; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT uq_user_question_attempt UNIQUE (user_id, question_id, attempt_number);


--
-- Name: usage_limits usage_limits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_limits
    ADD CONSTRAINT usage_limits_pkey PRIMARY KEY (id);


--
-- Name: user_subscriptions user_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_subscriptions
    ADD CONSTRAINT user_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_plans_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_plans_id ON public.plans USING btree (id);


--
-- Name: ix_usage_limits_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usage_limits_id ON public.usage_limits USING btree (id);


--
-- Name: ix_user_subscriptions_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_subscriptions_id ON public.user_subscriptions USING btree (id);


--
-- Name: flashcards flashcards_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.flashcards
    ADD CONSTRAINT flashcards_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.studysessions(id) ON DELETE CASCADE;


--
-- Name: flashcards flashcards_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.flashcards
    ADD CONSTRAINT flashcards_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: long_term_memory long_term_memory_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.long_term_memory
    ADD CONSTRAINT long_term_memory_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: messages messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.sessions(id) ON DELETE CASCADE;


--
-- Name: notes notes_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.studysessions(id) ON DELETE CASCADE;


--
-- Name: notes notes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notes
    ADD CONSTRAINT notes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: quiz_attempts quiz_attempts_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.quizzes(id) ON DELETE CASCADE;


--
-- Name: quiz_attempts quiz_attempts_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.studysessions(id) ON DELETE CASCADE;


--
-- Name: quiz_attempts quiz_attempts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quiz_attempts
    ADD CONSTRAINT quiz_attempts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: quizzes quizzes_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quizzes
    ADD CONSTRAINT quizzes_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.studysessions(id) ON DELETE CASCADE;


--
-- Name: quizzes quizzes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quizzes
    ADD CONSTRAINT quizzes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: studysessions studysessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.studysessions
    ADD CONSTRAINT studysessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: usage_limits usage_limits_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usage_limits
    ADD CONSTRAINT usage_limits_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_subscriptions user_subscriptions_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_subscriptions
    ADD CONSTRAINT user_subscriptions_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.plans(id) ON DELETE CASCADE;


--
-- Name: user_subscriptions user_subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_subscriptions
    ADD CONSTRAINT user_subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

