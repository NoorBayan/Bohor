# Bohor: A System for Extracting Arabic Poetic Metrical Patterns

<p align="center"> 
 <img src = "https://raw.githubusercontent.com/NoorBayan/Bohor/main/images/BohorLogo.png" width = "200px"/>
</p>

## Summary
**Bohor** is an advanced system designed for extracting and analyzing metrical patterns (taf'ilat) in classical Arabic poetry. By leveraging traditional works and advanced probabilistic modeling, Bohor provides a robust framework for understanding and generating poetic structures. This README outlines the development methodology, usage instructions, and contributions.

---

## Table of Contents
1. [Summary](#summary)
2. [Design Criteria](#design-criteria)
3. [Methodology](#methodology)
   - [1. Extraction and Organization of Prosodic Rules](#1-extraction-and-organization-of-prosodic-rules)
   - [2. Building a Mathematical Model for Pattern Generation](#2-building-a-mathematical-model-for-pattern-generation)
   - [3. Evaluation and Validation](#3-evaluation-and-validation)
4. [Use Cases for Bohor](#use-cases-for-bohor)
5. [How to Use Bohor](#how-to-use-bohor)
6. [Future Work](#future-work)
7. [Contributing](#contributing)
8. [License](#license)

---

## Design Criteria

The **Bohor corpus** plays a crucial role in preserving Arabic poetic heritage and facilitating access for analysis and appreciation. Effective design criteria for this corpus were established in collaboration with prosody experts and based on guidelines from the King Salman Center for Arabic Language. Key elements include **metrical feet** (تفعيلات), which are the rhythmic units forming Arabic poetic meters, represented by a coding scheme using "0" for consonants and "1" for vowels to aid computational analysis.

The criteria also cover **metrical substitutions** (زحافات) and **metrical modifications** (علل), as well as components such as **anchors** (أوتاد), **causes** (أسباب), and **separators** (فواصل), which form the rhythmic structure of poetic lines. Additionally, **rhyme structure** is examined through elements like **refrain** (روي), **support** (ردف), and **interior rhyme** (دخيل) to ensure cohesion and consistency in the poetic rhythm.

<p align="center"> 
 <img src = "https://raw.githubusercontent.com/NoorBayan/Bohor/main/images/BhoorCriteria.png" width = "800px"/>
</p>

---




## Methodology

The development of the "Bohor" Prosodic Patterns Corpus for classical Arabic poetry follows a comprehensive methodology based on King Salman Center for Arabic Language standards. This methodology involves three primary stages to ensure accurate prosodic pattern analysis and generation.

 <p align="center"> 
 <img src = "https://raw.githubusercontent.com/NoorBayan/Bohor/main/images/bhoor_methodology.png" width = "800px"/>
 </p>

### 1. Extraction and Organization of Prosodic Rules
The initial phase involves extracting prosodic rules for each poetic meter, including unique variations and exceptions. Based on six key references in Arabic prosody, this phase organizes rules into structured tables for efficient processing. The data includes essential details such as metrical feet patterns, caesura rules, and potential variations, creating a detailed base for computational analysis.

### 2. Building a Mathematical Model for Pattern Generation
This phase converts the extracted prosodic rules into a mathematical model capable of generating all possible rhythmic patterns for each poetic meter, accommodating unique variations and exceptions. Built in Python, the model uses decision tables for accurate prosodic representations and supports educational and analytical applications. The model is open source and can be used to analyze and interpret Arabic poetic forms in automated systems.

### 3. Evaluation and Validation
The final phase involves rigorous validation of the corpus by prosody experts to confirm accuracy. Computational tools are used to verify the model’s adherence to established prosodic rules, ensuring high-quality outputs. Extensive tests are conducted to confirm the corpus's accuracy in representing Arabic poetic weights and variations, establishing the corpus as a reliable tool for research and computational analysis.

This methodology ensures that the "Bohor" corpus serves as a comprehensive and precise resource for Arabic poetry analysis, supporting advanced research and computational applications.

---

## Use Cases for Bohor

The **Bohor** system will be utilized to build a comprehensive solution space named **Tafilat** for all taf'ilat patterns across various Arabic prosody systems. These systems include four main types:

- **Khalil Al-Farahidi System**: Contains 16 classical meters. This system is applied to classical Arabic poetry and a specific poetic genre known as "Qaseed."
- **Modern Meters**: Includes poetic meters added to Khalil Al-Farahidi's system, such as poems in colloquial Arabic dialects with unique meters invented by contemporary poets.
- **Adopted Meters**: Features poetic meters borrowed from the poetic traditions of other languages, such as "Dopplett," which many researchers believe was borrowed from Persian prosody systems.
- **Free Verse Meter System**: With the advent of modern free verse poetry, poems have evolved to adhere solely to taf'ilat without following traditional metrical patterns, allowing more flexibility and creativity.

The **Tafilat** solution space, which will be developed using Bohor, provides a structured approach to analyzing and generating these varied poetic forms. For more information and access to the solution space, visit [Tafilat](https://github.com/NoorBayan/Tafilat).

---

## How to Use Bohor

To get started with **Bohor**, follow these steps:

1. **Clone the repository**:
   To download the dataset, clone the repository to your local machine by running the following command:
   ```bash
   git clone https://github.com/NoorBayan/Bohor.git

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
