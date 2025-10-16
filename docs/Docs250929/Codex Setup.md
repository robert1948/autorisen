
#### I. Initial Connection and Access

* **Connect to GitHub:** For first-time use, you must **connect Codex to your GitHub repository**. This process is described as "super simple".  
* **Establish Environment:** Create your initial environment for the repository you wish Codex to work on.  
* **Set up Access Token (If Private):** If your repository is private, you will need to generate a **GitHub access token** and use it for authorization (e.g., in a workflow step like a `GET` webhook) to allow external systems access to your code.

#### II. Leveraging Context and Code Structure

* **Provide Code Context for Prompts (Advanced):** To ensure Codex receives the necessary context, you can access your committed code from GitHub by changing the 'G' in `GitHub` to a 'U' in the URL (e.g., `Uithub`) to get a flat text file of your code. This compressed view can be used to keep tokens optimal, especially as the repository grows.  
* **Utilize the Uithub API:** This feature has an API, allowing you to fully automate the process of grabbing the code context and integrating it into an enhanced prompt workflow.

#### III. Crafting Effective Prompts

When designing prompts, particularly if automating prompt generation using another model (like Gemini, as demonstrated in the sources), structure them clearly based on the recommended system instructions for Codex:

* **Focus on Single Tasks:** Avoid overwhelming Codex by focusing on **single task prompts**.  
* **Maintain Clarity and Precision:** Write prompts that are clear and precise, avoiding overly verbose descriptions.  
* **Use the Standard Prompt Format:** Structure your prompts with these three key components:  
  1. **The task:** Clearly define the coding goal.  
  2. **The location:** Specify the file paths (file locations) that Codex needs to work with.  
  3. **The goal:** Detail the desired outcome.

#### IV. Automating Workflow and Execution

* **Automate Prompt Generation (Recommended):** Use automation tools (like Zapier, connected to sources like Airtable and Gemini) to automatically create the enhanced prompt structure (Task, Location, Goal) whenever a feature request or bug fix is approved.  
* **Generate Quick-Launch Links:** Create a formatted URL link that pre-populates the prompt field in the Codex interface. This link should follow the format: `chatgpt.com/codex?prompt=` followed by the URL-encoded enhanced prompt.  
* **Execute and Merge:** Once a task is initiated by clicking the link and selecting "code", Codex will begin working in a virtual computer. Upon completion, Codex creates a pull request in your GitHub repo. You must then review and **merge the pull request** if the results are satisfactory.  
* **Run Tasks in Parallel:** Once you trust the prompt system and Codex, you can run \*\* multiple tasks at once\*\* (in parallel) to accelerate development.

