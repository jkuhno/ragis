# RAGIS (Retrieval-Augmented Generation Incident Summary)
Our project, RAGIS (Retrieval-Augmented Generation Incident Summary), helps security analysts determine whether an incident is a false positive or if the incident needs further investigation. It leverages generative AI and company data such as Microsoft Entra ID user details and previously closed incidents to make accurate predictions, saving valuable time and reducing the noise from false incidents.

## Inspiration
Security analysts often spend significant time investigating false positives, which can lead to inefficiencies. Studies show that nearly a third of their time is spent on incidents that pose no actual threat. This creates alert fatigue and slows down response times, motivating us to create a solution that reduces this burden and helps analysts focus on real security threats.

## How we built it
TODO:

## Setup
To use RAGIS, you need to get an Nvidia API Key and install NVIDIA AI Workbench. Optionally, you can also [query data from Azure](#optional:-azure-setup)

### API key

### NVIDIA AI Workbench

### OPTIONAL: Azure setup

<blockquote>
<details>
<summary>
Additional setup for integrating RAGIS with Azure
</summary>
    
RAGIS can be integrated with Azure to easily get all the data needed without saving copies of .csv files. RAGIS then can query background materials such as previously closed security incidents and Entra ID user details and also security alerts that are used as an input for RAGIS.

This guide provides step-by-step instructions on how to integrate RAGIS with Azure using a Service Principal in Microsoft Entra ID, previously known as Azure Active Directory (Azure AD).

### Prerequisites

Before starting the integration process, ensure you meet the following prerequisites:

- **Azure Subscription**: You must have an active Azure Subscription.
- **Permissions**: You need sufficient permissions to create a Service Principal within Entra ID (Azure AD).
- **Log Analytics Workspace**: You should already have a **Log Analytics Workspace** deployed.
- **Microsoft Sentinel**: Ensure Microsoft Sentinel is deployed and connected to your Log Analytics Workspace.
- For more details on how to deploy these resources, refer to the official [Microsoft Documentation](https://docs.microsoft.com/en-us/).

### Steps for Integrating RAGIS with Azure

#### 1. Create a Service Principal in Entra ID

A Service Principal is an identity created for use with applications, hosted services, and automated tools to access Azure resources.

##### Steps to Create a Service Principal:

1. **Sign in to Azure Portal**:
   - Go to [https://portal.azure.com](https://portal.azure.com) and log in with an account that has permission to create a Service Principal in Entra ID.

2. **Access Azure Active Directory**:
   - In the left-hand navigation pane, click on **Azure Active Directory**.

3. **Create a New Application**:
   - In the **Azure AD** blade, select **App registrations** from the left sidebar.
   - Click on **New registration** at the top.

4. **Configure the Application**:
   - Provide a name for the Service Principal, e.g., `sp-ragis`.
   - Under **Supported account types**, select **Accounts in this organizational directory only**.
   - Click **Register** to create the Service Principal.

#### 2. Create a Client Secret

After creating the Service Principal, you need to generate a **Client Secret** that will allow RAGIS to authenticate against Azure resources.

##### Steps to Create a Client Secret:

1. **Navigate to Certificates & Secrets**:
   - On the Service Principal’s overview page, click on **Certificates & secrets** in the left navigation pane.

2. **Create a New Client Secret**:
   - Under **Client secrets**, click **New client secret**.
   - Add a description (e.g., `RAGIS Client Secret`) and select an expiration time (e.g., 12 or 24 months).
   - Click **Add**.

3. **Save the Client Secret**:
   - After the secret is created, the value will be displayed. **Make sure to copy and save this value immediately**, as it will not be shown again.
   - This secret will be required later in NVIDIA AI Workbench as part of the environment configuration.

#### 3. Assign Permissions to the Service Principal

To allow the Service Principal to access the necessary resources, specific permissions must be granted. The Service Principal needs permissions to access user data and query Log Analytics data.

##### Assign **User.Read.All** Permissions (Microsoft Graph API):

1. **Navigate to API Permissions**:
   - On the Service Principal’s page, click **API permissions** in the left navigation pane.

2. **Add API Permissions**:
   - Click on **Add a permission**.
   - In the **Microsoft APIs** tab, select **Microsoft Graph**.

3. **Grant User.Read.All Permission**:
   - Choose **Application permissions**.
   - Search for and select **User.Read.All** permission.
   - Click **Add permissions**.

4. **Grant Admin Consent**:
   - After adding the permissions, click the **Grant admin consent for [your directory]** button to approve these permissions. You must have admin rights to grant consent.

##### Assign Log Analytics Reader Role:

The Service Principal also needs to be able to query data from the Log Analytics Workspace.

1. **Assign Log Analytics Reader Role**:
   - Go to the **Log Analytics Workspace** you are using with Sentinel.
   - In the **Access control (IAM)** tab, click on **Add role assignment**.
   - Search for the **Log Analytics Reader** role and select it.
   - Assign the role to the Service Principal you created earlier (search by name or Client ID).

#### 4. Save the Service Principal Details for NVIDIA AI Workbench

After configuring the Service Principal, you will need to collect the following information for use in NVIDIA AI Workbench.

##### Collect and Save the Following Information:

- **Client ID**: Found on the Service Principal’s overview page.
- **Tenant ID**: Found on the Service Principal’s overview page.
- **Client Secret**: Created in the previous step.

You will need to store these values as environmental secrets within the NVIDIA AI Workbench. This will allow RAGIS to authenticate as a service principal and query data from Azure Log Analytics Workspace.

#### 5. Configure RAGIS to Query Log Analytics Data

Once the Service Principal is created and the necessary permissions are granted, RAGIS can be configured to use it for querying data from the Log Analytics Workspace.

1. **Save the Workspace ID in RAGIS**:
   - The **Log Analytics Workspace ID** needs to be saved in RAGIS Azure tab.

2. **Query Data**:
   - RAGIS can now use the Service Principal to query the data:
     - **Security Alerts**: Used as input for RAGIS analysis.
     - **Closed Incidents**: Used as background material for RAGIS
     - **Entra ID user details**: Used as a background material for RAGIS

Make sure to keep all the secret credentials safe and secure, and regularly update them if needed to maintain continuous operation of the system.

</details>
</blockquote>