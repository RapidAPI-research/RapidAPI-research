# A First Look at Security and Privacy Risks in the RapidAPI Ecosystem

## Abstract
The RapidAPI platform is one of the largest API platforms and it provides over 40,000 APIs, which have been used by more than 4 million developers. Third-party developers can publish their APIs on the RapidAPI platform, facilitating development and increasing the diversity of available services. However, such a paradigm also raises security and privacy concerns associated with APIs hosted on the platform. In this work, we perform the first large-scale analysis of 32,089 APIs on the RapidAPI platform. By searching in the GitHub code and Android apps, we find that 3,533 RapidAPI keys, which are important and used in API request authorization, have been leaked in the wild. These keys can be exploited to launch various attacks, such as Resource Exhaustion Running, Theft of Service, Data Manipulation, and User Data Breach attacks. We also explore risks in API metadata that can be abused by adversaries. Due to the lack of a strict certification system, adversaries can manipulate the API metadata to perform typosquatting attacks on API URLs, impersonate other developers or renowned companies, and publish spamming APIs on the platform. Lastly, we analyze the privacy non-compliance of APIs and applications, e.g., Android apps, that call these APIs with data collection. We find that 1,709 APIs collect sensitive data and 94% of them don’t provide a complete privacy policy. In Android apps, 50% of apps that call these APIs have privacy non-compliance issues.


## Key Leaks in the Wild

We find that 3,533 keys used for API request authorization have been leaked by developers in GitHub or Android code. We demonstrate that adversaries can utilize the leaked keys to launch four attacks, e.g., Resource Exhaustion Running attack, Theft of Service attack, Data Manipulation attack, and User Data Breach attack.

![key_leaks](https://github.com/RapidAPI-research/RapidAPI-research/blob/main/images/all_attacks.png)

## Risks of API Metadata Abuse
We discover the risks of API metadata abuse. Due to the poor certification process in the RapidAPI platform, adversaries can publish any APIs on the platform, such as typosquatting APIs to attack other APIs or spamming APIs for product promotion. Malicious developers can also impersonate famous companies and mislead developers into calling their APIs.

### Typosquatting on Endpoints URLs

![typosquatting](https://github.com/RapidAPI-research/RapidAPI-research/blob/main/images/squatting.png)

### Developers Impersonation
![developer](https://github.com/RapidAPI-research/RapidAPI-research/blob/main/images/developer.png)

### Spamming APIs
![spamming](https://github.com/RapidAPI-research/RapidAPI-research/blob/main/images/spamming.png)

## Privacy Non-Compliance of Rapid APIs
We analyze the privacy compliance of APIs on the RapidAPI platform and Android apps that call these APIs. We find 1,709 APIs that collect sensitive data and 94% APIs don’t provide a complete privacy policy although they are supposed to do so. By analyzing the source code and privacy policies of Android apps, we find that 50% of Android apps calling data collection APIs don’t provide a complete privacy policy.

### Privacy Non-Compliance in Rapid APIs

![pp](https://github.com/RapidAPI-research/RapidAPI-research/blob/main/images/privacy_policy.png)

### Privacy Non-Compliance in Applications Calling Rapid APIs
As a result, we found 526 out of 1 million Android apps calling 316 APIs on the RapidAPI platform. As for data collection behaviors, we found 54 apps calling 11 APIs that collect data. Among them, 16 apps lack a privacy policy, 11 apps have an incomplete privacy policy, and only 27 apps (50%) have a complete privacy policy.
