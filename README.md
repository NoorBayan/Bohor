# Bohor: A System for Extracting Arabic Poetic Metrical Patterns

 <p align="center"> 
 <img src = "https://raw.githubusercontent.com/NoorBayan/Bohor/main/images/BohorLogo.png" width = "200px"/>
 </p>

## Summary
**Bohor** is an advanced system designed for extracting and analyzing metrical patterns (taf'ilat) in classical Arabic poetry. By leveraging traditional works and advanced probabilistic modeling, Bohor provides a robust framework for understanding and generating poetic structures. This README outlines the development methodology, usage instructions, and contributions.

---

## Table of Contents
1. [Summary](#summary)
2. [Methodology](#methodology)
   - [Step 1: Extracting Basic Taf'ilat Patterns](#step-1-extracting-basic-tafilat-patterns)
   - [Step 2: Building the Probability Model](#step-2-building-the-probability-model)
   - [Step 3: Handling Exceptional Cases](#step-3-handling-exceptional-cases)
   - [Step 4: Processing Rhyme Patterns](#step-4-processing-rhyme-patterns)
   - [Step 5: Generating Taf'ilat Patterns](#step-5-generating-tafilat-patterns)
3. [Use Cases for Bohor](#use-cases-for-Bohor)
4. [How to Use Bohor](#how-to-use-Bohor)
5. [Future Work](#future-work)
6. [Contributing](#contributing)
7. [License](#license)

---

## Methodology

 <p align="center"> 
 <img src = "https://raw.githubusercontent.com/NoorBayan/Bohor/main/images/BohorMethodology.png" width = "500px"/>
 </p>
 
The development of the **Bohor** system involves a systematic approach, broken down into five key steps:

### Step 1: Extracting Basic Taf'ilat Patterns
In this phase, we extract the fundamental taf'ilat patterns based on the analysis of six traditional Arabic prosody works considered gold standards. The primary reference used is "القواعد العروضية وأحكام القافية العربية" (The Rules of Prosody and Arabic Rhyme). This work is supplemented by five additional references to extract the core patterns and rules from which sub-patterns will be developed.

### Step 2: Building the Probability Model
This step involves constructing a probabilistic model to compute possible sub-patterns based on the basic rules identified in Step 1. The core rules are transformed into a probabilistic framework to generate potential taf'ilat patterns for each poetic meter.

### Step 3: Handling Exceptional Cases
Based on the six traditional prosody works, we study and analyze exceptional cases that fall outside the standard rules, as well as modern poetic deviations. These exceptional cases are integrated into the probability model to ensure comprehensive coverage of all possible patterns.

### Step 4: Processing Rhyme Patterns
Rhyme patterns are extracted from the final taf'ilat of the poetic line based on specific conditions. Utilizing the six references, we study various Arabic rhyme rules and apply them to the taf'ilat pattern base. For example, the rhyme of a poetic line can be derived from the last consonant in the line to the consonant preceding it, shaping the taf'ilat patterns accordingly.

![Step 4: Processing Rhyme Patterns](path_to_image_step_4)

### Step 5: Generating Taf'ilat Patterns
In this final step, we generate taf'ilat patterns for each poetic meter, ensuring that any poetic line composed adheres to these patterns. This guarantees that the generated patterns align with the established metrical rules.

---

## Use Cases for Bohor

The **Bohor** system will be utilized to build a comprehensive solution space named **Tafilat** for all taf'ilat patterns across various Arabic prosody systems. These systems include four main types:

- **Khalil Al-Farahidi System**: Contains 16 classical meters. This system is applied to classical Arabic poetry and a specific poetic genre known as "Qaseed."
- **Modern Meters**: Includes poetic meters added to Khalil Al-Farahidi's system, such as poems in colloquial Arabic dialects with unique meters invented by contemporary poets.
- **Adopted Meters**: Features poetic meters borrowed from the poetic traditions of other languages, such as "Dopplett," which many researchers believe was borrowed from Persian prosody systems.
- **Free Verse Meter System**: With the advent of modern free verse poetry, poems have evolved to adhere solely to taf'ilat without following traditional metrical patterns, allowing more flexibility and creativity.

The **Tafilat** solution space, which will be developed using Bohor, provides a structured approach to analyzing and generating these varied poetic forms. For more information and access to the solution space, visit [Tafilat](https://github.com/yourusername/Tafilat).

---

## How to Use Bohor

To get started with **Bohor**, follow these steps:

1. **Clone the repository**:
   To download the dataset, clone the repository to your local machine by running the following command:
   ```bash
   git clone https://github.com/yourusername/Bohor.git

2. **Access detailed instructions**:
   For comprehensive guidelines on how to use the dataset, including sample code and practical applications, visit the [Google Colab notebook](https://colab.research.google.com/your-notebook-link), where you’ll find step-by-step instructions.

---

## Future Work
The **TAFILAT** dataset is a foundational tool for Arabic meter research, and we envision several future expansions, including:

- **Incorporating Modern Meters**: Extending the dataset to include modern Arabic meters that are used in free verse and contemporary poetry, allowing a more comprehensive analysis.
- **Enhancing Prosodic Visualization**: Developing visual tools to represent taf’ilat patterns interactively, aiding in the intuitive understanding of complex poetic structures.
- **Integration with Generative AI**: Combining the dataset with AI models to create automated Arabic poem generation systems that follow classical metrical rules.
- **Expansion to Other Dialects**: Including meters from Arabic dialectal poetry and prosodic patterns in non-classical forms, enriching the dataset for broader applications.

## Contributing
We welcome contributions from the community! Whether you are an expert in Arabic prosody, a data scientist, or a developer interested in enhancing this dataset, your input is valuable. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes and add tests if applicable.
4. Submit a pull request with a detailed description of your changes.

Please refer to our [CONTRIBUTING.md](CONTRIBUTING.md) file for more information.

## License
The **TAFILAT** dataset is open-source and is licensed under the [MIT License](LICENSE.md). Feel free to use, modify, and distribute the dataset in your research or applications, as long as proper attribution is given.
