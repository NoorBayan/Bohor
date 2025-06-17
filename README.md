# Bohor: A Prosodic Corpus of Arabic Meters and Rhythmic Variants

<p align="center"> 
 <img src = "https://raw.githubusercontent.com/NoorBayan/Bohor/main/images/BohorLogo.png" width = "200px"/>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.YOUR_ACTUAL_DOI.svg)](https://doi.org/10.5281/zenodo.15615402) 
<!-- Add other badges if relevant, e.g., for an arXiv preprint if you have one -->

Welcome to the **Bohor (بُحُور)** corpus project! Bohor is a meticulously crafted, machine-readable dataset designed to capture the rich and intricate system of classical Arabic poetry's meters (known as *buḥūr*). This resource aims to empower researchers, linguists, and developers in the fields of computational linguistics, digital humanities, and Arabic literature studies.

## Table of Contents

- [What is Bohor?](#what-is-bohor)
- [Core Objectives](#core-objectives)
- [Key Highlights](#key-highlights)
- [Dataset Overview](#dataset-overview)
  - [Content and Scope](#content-and-scope)
  - [Data Format](#data-format)
- [Getting Started](#getting-started)
  - [Accessing the Data](#accessing-the-data)
  - [Exploring with Google Colab](#exploring-with-google-colab)
- [Potential Use Cases](#potential-use-cases)
- [How to Contribute](#how-to-contribute)
- [Contact & Support](#contact--support)

## What is Bohor?

The Bohor corpus offers a deep and structured representation of the 16 canonical meters of classical Arabic poetry, as established by the foundational work of Al-Khalil ibn Ahmad al-Farahidi. Unlike many existing resources that focus primarily on high-level meter classification, Bohor delves into the granular details of prosodic structure, including:

*   **Metrical Feet (Tafʿīlāt - تفعيلات):** The fundamental rhythmic units.
*   **Permissible Variations (Zihāfāt - زحافات & ʿIlāl - علل):** The subtle yet crucial modifications that poets use to achieve rhythmic diversity and expressiveness.
*   **Rhyme System (Qāfiyah - قافية):** Detailed components and rules governing poetic rhyme.

Our goal is to provide a definitive, computationally accessible reference for the theoretical space of Arabic prosody.

## Core Objectives

*   **To provide an exhaustive inventory:** Cataloging all theoretically valid metrical patterns based on classical prosodic rules.
*   **To facilitate fine-grained analysis:** Enabling detailed scansion and rhythmic study beyond simple meter identification.
*   **To support AI and NLP development:** Offering a robust dataset for training and evaluating computational models for Arabic poetry.
*   **To bridge traditional scholarship and modern computation:** Translating classical prosodic knowledge into a structured, machine-readable format.
*   **To promote open research:** Making this valuable resource freely available to the academic community.

## Key Highlights

*   **Unprecedented Granularity:** Detailed encoding of metrical feet, their transformations, sub-syllabic components, and rhyme structures.
*   **Theoretical Rigor:** Grounded in seven authoritative classical Arabic prosody treatises.
*   **Systematic Generation & Validation:** Patterns were algorithmically generated based on a formal mathematical model and subsequently validated through expert review and empirical testing.
*   **Probabilistic Ranking for Ambiguity:** Includes a mechanism to suggest the most likely scansion for metrically ambiguous lines based on statistical analysis of attested poetic usage.
*   **Focus on Vocalized Input:** Designed to work with fully diacritized Arabic poetry, ensuring prosodic precision.
*   **Machine-Readiness:** Structured data formats for easy integration into computational workflows.

## Dataset Overview

### Content and Scope

The Bohor corpus encompasses:

*   **16 Canonical Meters:** All traditional meters defined by Al-Khalil.
*   **24 Meter Variants:** Including structurally distinct sub-forms (e.g., *tāmm* - complete, *majzūʾ* - catalectic).
*   **Over 78000 Unique Metrical Patterns:** Each pattern represents a valid sequence of *tafʿīlāt* with their allowed variations.
*   **Detailed Annotations for each pattern:**
    *   Rhythmic encoding (binary-like representation of short/long syllables).
    *   Type of metrical transformation applied (*zihāf*, *ʿilal*, or intact).
    *   Decomposition into prosodic sub-units (*awtād*, *asbāb*, *fawāṣil*).
    *   Information related to the *qāfiyah* (rhyme) system.

### Data Format

*(This section requires your specific details. Below is an example; please adapt it accurately.)*

The primary data is provided in **JSON format**, with individual files for each of the 24 meter variants (e.g., `Al_Tawil_Tamm_patterns.json`, `Al_Kamil_Majzu_patterns.json`). Each JSON file contains a list of pattern objects. A pattern object typically includes fields like:

*   `pattern_id`: A unique string identifying the pattern within its meter variant.
*   `meter_name_ar`: Arabic name of the base meter (e.g., "الطويل").
*   `meter_name_en`: English transliteration of the base meter (e.g., "Al-Ṭawīl").
*   `meter_variant_ar`: Arabic name of the meter variant (e.g., "تام").
*   `meter_variant_en`: English transliteration of the meter variant (e.g., "Tāmm").
*   `hemistich_1_tafilat`: A list of *tafʿīlah* objects for the first hemistich.
*   `hemistich_2_tafilat`: A list of *tafʿīlah* objects for the second hemistich.
*   `rhyme_details`: (Optional) An object containing rhyme information if applicable at this level.

Each *tafʿīlah* object within the hemistich lists contains:

*   `name_ar`: Arabic name of the *tafʿīlah* (e.g., "فعولن").
*   `name_en`: English transliteration (e.g., "Faʿūlun").
*   `rhythmic_encoding`: The binary-like string (e.g., "010110").
*   `transformation_type`: Type of metrical change (e.g., "Intact", "Zihāf", "ʿIlal").
*   `specific_transformation_ar`: Arabic name of the specific *zihāf* or *ʿilal* if any (e.g., "قبض").
*   `specific_transformation_en`: English transliteration of the transformation.
*   `sub_units`: A list of prosodic sub-units (*awtād*, *asbāb*, *fawāṣil*) forming the *tafʿīlah*.


## Getting Started

This section guides you on how to access and begin exploring the Bohor corpus.

### Accessing the Data

There are two primary ways to obtain the Bohor corpus:

1.  **Clone the GitHub Repository:**
    This method gives you the latest version of the corpus files along with any accompanying scripts or notebooks.
    Open your terminal or command prompt and run the following command:
    ```bash
    git clone https://github.com/NoorBayan/Bohor.git
    ```
    After cloning, navigate into the newly created directory:
    ```bash
    cd Bohor
    ```
    You will find the corpus data typically within a `/corpus` or `/data` subdirectory (please check the `Dataset Overview` section above or the repository structure for the exact path).

2.  **Download from Zenodo (Recommended for Archival Version):**
    For a stable, versioned, and citable version of the dataset, we recommend downloading it from our Zenodo archive. This is particularly useful if you need to reference a specific release of the corpus in your research.
    
    *   **Zenodo DOI:** [https://doi.org/10.5281/zenodo.YOUR_ACTUAL_DOI](https://doi.org/10.5281/zenodo.YOUR_ACTUAL_DOI) 
        *(Replace `YOUR_ACTUAL_DOI` with the actual DOI assigned to your dataset on Zenodo.)*
    
    Visit the link above to access the download options for the corpus files.

### Exploring with Google Colab
### 📘 Exploring with Google Colab

To support in-depth and accessible engagement with the **Bohor Prosodic Corpus**, we provide a set of curated **Google Colab notebooks**. These notebooks are designed to assist linguists, computational researchers, educators, and students in exploring the corpus, its structure, and its downstream applications in classical Arabic prosody.

Each notebook serves a distinct research or educational purpose, and includes annotated code, visualizations, and interactive outputs.

---

#### 🔹 1. Exploring Prosodic Pattern Structures

This notebook provides a hands-on interface to explore the **metrical patterns** (`tafʿīlāt`) generated by the Bohor corpus. Users can load specific meters, visualize all valid rhythmic variations (including `zihāfāt` and `ʿilāl`), and investigate how each pattern is constructed from its prosodic components (`awtād`, `asbāb`, `fawāṣil`).

- **Ideal for**: students of Arabic prosody, computational linguists interested in metrical representations, and AI researchers working on rhythm modeling.
- **Features**:
  - Load metrical decision tables for any classical meter
  - Visualize tafʿīlāt structure as annotated sequences
  - Explore rule-based transformations

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1RN4YVoUBpi2ToV6kLNjXmqZeugfzV-do?usp=sharing)

<p align="center">
  <img src="docs/images/pattern_exploration_preview.png" width="720">
</p>

---

#### 🔹 2. Corpus Overview and Metadata Exploration

This notebook allows users to explore the **Bohor corpus dataset** itself. It includes full access to metrical annotations, meter labels, rhyme components, and tafʿīlah-level breakdowns across all supported meters.

- **Ideal for**: corpus linguists, digital humanities researchers, and educators designing curricula for Arabic poetics.
- **Features**:
  - Inspect metadata and corpus statistics
  - Filter by meter, rhythmic pattern, or rhyme type
  - Analyze frequency distributions of metrical forms

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1F3LDGBc23lytjxnQWjs4xG9RC4TKmC_H?usp=sharing)

 <p align="center">
   <img src = "https://raw.githubusercontent.com/NoorBayan/Tafilat/main/images/TafilatColab.png" width = "600px"/>
 </p>

---

#### 🔹 3. Analyzing 30,000+ Scanned Classical Poems

This notebook provides access to a large-scale dataset of **over 30,000 classical Arabic poems** that have been automatically scanned using the Bohor system. It enables empirical analysis of metrical usage, meter diversity, and rhythmic irregularities.

- **Ideal for**: data scientists, poetic stylometry researchers, and students studying diachronic prosodic trends.
- **Features**:
  - Query by poet, era, or meter
  - Visualize metrical diversity and patterns per corpus subset
  - Compare scanned outputs against the Bohor pattern reference

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1D5XsvnXQoIcWc53ef1EcH6A6uwYFe2Pr?usp=sharing)

 <p align="center">
   <img src = "https://raw.githubusercontent.com/NoorBayan/Awzan/main/images/AwzanColab.png" width = "1000px"/>
 </p>

---

#### 🔹 4. Farāhīdī System Output Viewer

This notebook demonstrates a sample of the **output generated by the Farāhīdī computational system** described in the paper. It showcases how raw verse input is processed into multi-layered annotated metrical structures, validated against the Bohor corpus.

- **Ideal for**: NLP practitioners, tool developers, and those interested in computational modeling of poetic form.
- **Features**:
  - Step-by-step transformation of verse into metrical structure
  - Pattern-matching with the Bohor corpus
  - Visualization of tafʿīlāt and rhyme analysis

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1zlZqghXIlpe6tIsk6Q6lpNDSkkDA1mZZ?usp=sharing)



 <p align="center">
   <img src = "https://raw.githubusercontent.com/NoorBayan/Frahidi/main/images/FarahidiColab.png" width = "800px"/>
 </p>
---

💡 **Note**: All notebooks are written in Python and compatible with Google Colab. No local installation is required—just open, run, and explore.


## Potential Use Cases

The Bohor corpus, with its depth and structured nature, is designed to be a valuable asset for a wide array of research, development, and educational activities related to classical Arabic poetry. Potential applications include, but are not limited to:

*   **Advanced Prosodic Analysis Tools:**
    *   Developing sophisticated parsers for fine-grained scansion of Arabic verse, identifying not just the base meter but the specific *tafʿīlāt* and their variations (*zihāfāt* and *ʿilāl*).
    *   Tools for automatic detection of metrical errors or deviations from canonical patterns.

*   **Computational Stylistics and Literary Studies:**
    *   Conducting large-scale quantitative analyses of metrical styles across different poets, historical periods, or literary genres.
    *   Investigating the evolution of metrical practices and the prevalence of specific rhythmic variations over time.
    *   Exploring correlations between metrical features and thematic content or poetic intent.

*   **AI-Powered Poetry Generation and Creativity:**
    *   Utilizing Bohor as a rich knowledge base or a set of valid rhythmic templates for AI systems that generate classical Arabic poetry.
    *   Employing the corpus as a stringent validation filter to ensure the metrical correctness of machine-generated verse.
    *   Facilitating constrained data augmentation by filling metrically valid templates with coherent content.

*   **Evaluation and Benchmarking of AI Models:**
    *   Serving as a gold-standard reference to assess the metrical accuracy and prosodic understanding of Large Language Models (LLMs) and other AI models tasked with poetry-related tasks.

*   **Digital Pedagogy and Educational Resources:**
    *   Underpinning interactive e-learning platforms and software for teaching and learning Arabic prosody (ʿIlm al-ʿArūḍ).
    *   Providing students with a comprehensive resource to explore metrical patterns and their permissible transformations.

*   **Linguistic Research:**
    *   Studying the combinatorial properties, constraints, and generative capacity of the Arabic metrical system from a formal linguistic perspective.
    *   Investigating the relationship between prosody, morphology, and syntax in Arabic poetry.

*   **Enhancing NLP Tools for Arabic:**
    *   Informing the development of more accurate automated diacritization (vocalization) tools specifically for poetic texts, by using Bohor's patterns to bias towards metrically sound vocalizations.


## How to Contribute

We enthusiastically welcome contributions from the research community and developers to help improve and expand the Bohor corpus and its associated resources! Your expertise and insights can significantly enhance this project. Here are several ways you can contribute:

*   **Reporting Bugs or Issues:**
    If you encounter any errors, inaccuracies, or inconsistencies in the corpus data, documentation, or the provided Colab notebook, please [submit an issue](https://github.com/NoorBayan/Bohor/issues). Be sure to provide detailed information, including steps to reproduce the issue if applicable.

*   **Suggesting Enhancements or New Features:**
    Do you have ideas for additional annotations, new metrical patterns (backed by scholarly sources), improvements to the data structure, or useful tools that could be built around Bohor? We encourage you to [open an issue](https://github.com/NoorBayan/Bohor/issues) to discuss your suggestions.

*   **Code Contributions (Pull Requests):**
    If you'd like to contribute code—such as new scripts for analysis, improved visualization tools, or enhancements to the data generation/validation process—please follow these general steps:
    1.  Fork the repository.
    2.  Create a new branch for your feature or bugfix (`git checkout -b feature/your-feature-name`).
    3.  Make your changes and commit them with clear, descriptive messages.
    4.  Push your changes to your forked repository.
    5.  Submit a pull request to the `main` branch of the official Bohor repository.
    We recommend discussing significant changes in an issue before starting extensive work.

*   **Improving Documentation:**
    Clear documentation is crucial. If you find areas in the `README.md` or other documentation that could be clarified or expanded, please suggest changes by opening an issue or submitting a pull request.

*   **Sharing Use Cases and Derivative Works:**
    If you use Bohor in your research or develop interesting applications or derivative datasets, we would be delighted to hear about it! Consider sharing your work with the community (e.g., by linking to it in a GitHub issue or contacting us).

We aim to create a collaborative environment. For more detailed contribution guidelines (e.g., coding style, commit message conventions), please refer to our (forthcoming) `CONTRIBUTING.md` file. *(You may want to create this file later as the project grows.)*

## Contact & Support

We are committed to supporting users of the Bohor corpus. For questions, feedback, or assistance, please reach out through the following channels:

*   **GitHub Issues (Primary Channel for Technical Support & Bug Reports):**
    For any technical difficulties, bug reports, feature requests, or specific questions about the data, the most effective way to get support is by [opening an issue on our GitHub repository](https://github.com/NoorBayan/Bohor/issues). This allows the discussion to be tracked publicly and benefit other users.

