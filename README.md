# Boardgames Analysis
## Data Engineer Zoomcamp Capstone Project

This capstone project was developed under the scope of the [Data Engineer Zoomcamp by DataTalksClub](https://github.com/DataTalksClub/data-engineering-zoomcamp) (the biggest Data community in the internet - [DTC](https://datatalks.club/).

The above zoomcamp had the following main topics/tools:
- Docker and docker-compose;
- Google Cloud Platform;
- Terraform;
- Airflow;
- Data Warehouse with Big Query;
- Analytics Engineering with Data Build Tool (DBT);
- Batch with Spark;
- Streaming with Kafka.

The zoomcamp is completed with a personal [Project](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/week_7_project) envolving some of those tools/topics.

For my project I decided to analyse the boardgames published till today (around 130k) and their respective prices from 8 online stores with price alert notification via e-mail.

**With this project I intend to analyse the boardgame universe, checking the trend of boardgames published with their respetive price ranges and giving the possibility to define a wishlist of boardgames with the target price.**

![Takenoko](https://www.boardgamequest.com/wp-content/uploads/2015/09/Takenoko-Chibis-Header.jpg)

## Dataset

In terms of dataset I used the main database available online that is recognized by the boardgaming community worldwide known as [BoardGameGeek](https://boardgamegeek.com/) and performed web scraping techniques to extract the desired data.

To extract the data from online stores, I used a price comparison website for boardgames called [Ludonauta](https://www.ludonauta.es/) to get the information from the following stores:
- [Espacio de Juegos](https://www.espaciodejuegos.es/)
- [Jugamos Otra?](https://jugamosotra.com/es/)
- [jugarXjugar](https://www.jugarxjugar.com/shop/)
- [Doctor Panush](https://doctorpanush.com/)
- [El Dado Negro](https://eldadonegro.com/)
- [Fdgames](https://fdgames.eu/es/)
- [SomosJuegos](https://www.somosjuegos.com/)
- [Mathom](https://mathom.es/es/)

## Used Technologies ????

For this project I decided to use the following tools:
- Docker - to proceed to the containerization of other technologies;
- Airflow - for the orchestration of the full pipeline;
- Terraform - As a Infrastructure-as-Code (IaC) tool;
- Google Cloud Storage (GCS) - for storage as Data Lake;
- BigQuery- for the project Data Warehouse;
- Data Build Tool (DBT) - for the transformation of raw data in refined data;
- Google Data studio - for visualizations.

# Reproduce the project

## Prerequisites

The following requirements are needed to reproduce the project:

1. A [Google Cloud Platform](https://cloud.google.com/) account.
2. (Optional) The [Google Cloud SDK](https://cloud.google.com/sdk). Instructions for installing it are below.
    * Most instructions below will assume that you are using the SDK for simplicity.
    * If you use a VM instance on Google Cloud Platform the Google Cloud SDK comes installed by default, don't have to perform this step.
3. (Optional) A SSH client.
    * All the instructions listed below assume that you are using a Terminal and SSH.
    * I'm using Git Bash where you can donwload [here](https://gitforwindows.org/).
4. (Optional) VSCode with the Remote-SSH extension.
    * Any other IDE should work, but VSCode makes it very convenient to forward ports in remote VM's.
5. A [DBT cloud account](https://www.getdbt.com/signup/) and connect to your BigQuery [following these instructions](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/week_4_analytics_engineering/dbt_cloud_setup.md).

Development and testing were carried out using a Google Cloud Compute VM instance. I strongly recommend that a VM instance is used for reproducing the project as well. All the instructions below will assume that a VM is used.


## Create a Google Cloud Project

Access the [Google Cloud dashboard](https://console.cloud.google.com/) and create a new project from the dropdown menu on the top left of the screen, to the right of the _Google Cloud Platform_ text.

## Create a Service Account
After you create the project, you will need to create a _Service Account_ with the following roles:
* `BigQuery Admin`
* `Storage Admin`
* `Storage Object Admin`
* `Viewer`

- To create a _Service Account_ go to Google Cloud Platform console and in the left panel select the option **IAM & Admin -> Service Accounts**
![myimage-alt-tag](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/d5b9ab26-7af8-4ef3-b971-e82e12bcb5da/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220619T150720Z&X-Amz-Expires=86400&X-Amz-Signature=f80233664796347aba231819eb8a396321b02138bec8eacce5659903e45d3cc4&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)
- Click on **Create Service Account**
- Define a Service account name and description to help you describe what this service account will do
- On step 2 add the following roles showed on the printscreen below:
![myimage-alt-tag](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/0898ae67-b14f-4f48-b0ab-0197a950b40e/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220619T151002Z&X-Amz-Expires=86400&X-Amz-Signature=aac1fc048c10d20f9f01cb4d25eccf2cff6d48e4288b1f5aa8e4cebb75ed30d1&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)

- In the Service account dashboard click on **Actions -> Manage keys**
![myimage-alt-tag](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/9691989d-7cfb-4013-9ff8-71da9f7ee631/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220619T152345Z&X-Amz-Expires=86400&X-Amz-Signature=845261f1b2c3dbdefd4a4749e653c3d1c2d741b708e6ba20b7013506b0b0f445&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)
- Click on **Add key -> Create new key**
![myimage-alt-tag](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/5bf297b4-5610-4606-a384-f3ecda1f85ab/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220619T152416Z&X-Amz-Expires=86400&X-Amz-Signature=b6dec19b800cbf58b3c605334ad295ef9e1ee314e2d8fdec7aa0062de0ea99e1&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)
- Choose key type **JSON** and click on Create
![myimage-alt-tag](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/13cd5f6b-41fc-4ef0-b1e7-63e62b865fd4/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220619T152443Z&X-Amz-Expires=86400&X-Amz-Signature=e1a6ec8263d94aa91258dbcee6632687c592f860d52b3ded96b4212fc4fd5220&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)
- When saving the file rename it to `google_credentials.json` and store it in your home folder, in `$HOME/.google/credentials/` .
> ***IMPORTANT***: if you're using a VM as recommended, you will have to upload this credentials file to the VM.

You will also need to activate the following APIs:
* https://console.cloud.google.com/apis/library/iam.googleapis.com
* https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com

## Generate a SSH Key

- Create a .ssh directory using Git Bash if you're on a Windows environment
- ```cd .ssh ```
- Run the command changing to the desired **KEY_FILENAME** and **USER** ```ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USER -b 2048```
- A file with the structure **key_filename.pub** is saved into the .ssh folder
- Now we have to put the public key in Google Cloud Platform
- Go to Navigation Menu -> Compute Engine -> Metadata
- Print the key using bash command in your environment: ```cat key_filename.pub ```
- Copy the value to GCP and save

## (Optional) Install and setup Google Cloud SDK
**Note**: This step is only required if you don't use a Virtual Machine instance on Google Cloud Platform, because in that case the software is already installed.
1. Download Gcloud SDK [from this link](https://cloud.google.com/sdk/docs/install) and install it according to the instructions for your OS.
1. Initialize the SDK [following these instructions](https://cloud.google.com/sdk/docs/quickstart).
    1. Run `gcloud init` from a terminal and follow the instructions.
    1. Make sure that your project is selected with the command `gcloud config list`

## Creating a Virtual Machine on GCP
1. From your project's dashboard, go to _Cloud Compute_ > _VM instance_
1. Create a new instance:
    * Any name of your choosing
    * Pick your favourite region. You can check out the regions [in this link](https://cloud.google.com/about/locations).
        > ***IMPORTANT***: make sure that you use the same region for all of your Google Cloud components.
    * Pick a _E2 series_ instance. A _e2-standard-4_ instance is recommended (4 vCPUs, 16GB RAM)
    * Change the boot disk to _Ubuntu_. The _Ubuntu 20.04 LTS_ version is recommended. Also pick at least 30GB of storage.
    * Leave all other settings on their default value and click on _Create_.

## Set up SSH access to the VM

1. Start your instance from the _VM instances_ dashboard in Google Cloud.
1. Copy the external IP address from the _VM instances_ dashboard.
2. Go to the terminal and type ```ssh -i ~/.ssh/gcp username@external_ip``` where gcp corresponds to the _key_filename_.

## Creating SSH config file

1. Open a Git Bash terminal
2. Change to the folder .ssh: ```cd .ssh```
3. Create a configuration file: ```touch config```
4. Open the configuration file with your default IDE (in my case is VSCode): ```code config```
5. Insert the following code changing the name, IP address, user and IdentityFile to your own
```
Host de-zoomcamp
    Hostname 34.77.77.161
    User u10054206
    IdentityFile C:/Users/u10054206/.ssh/gcp
```
6. Execute the ssh command to connect to the Virtual Machine using alias name
```ssh de-zoomcamp```
- **Note**: When you stop the VM instance, the external IP address can change, in that case you have to perform the steps 4-6 again updating to the new IP address.

## (Optional) Configure VSCode to access VM in Google Cloud Platform
1. Open VSCode
2. Go to extensions on the left panel
3. Search for remote ssh and install the following extension

![myimage-alt-tag](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/f6df8c15-eaa3-49ec-a759-993278de8708/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220619T095307Z&X-Amz-Expires=86400&X-Amz-Signature=8891d0b2d39840d4c24c64533b67bacc2c9e55fd137962b39f50f63732d16bf3&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)

4. Open the remote window, clicking on the left bottom green button

![myimage-alt-tag](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/d5d46474-ff80-4849-a0ae-48e1b40735fa/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220619T095632Z&X-Amz-Expires=86400&X-Amz-Signature=11e065349ef9df173ebdd94c9030fe092118573c8004fa1ff1646657225e46f6&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)

5. Select **Connect to host...** option
![myimage-alt-tag](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/e8a1c07d-aac1-493a-a917-0799e02f068a/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220619T095718Z&X-Amz-Expires=86400&X-Amz-Signature=75c8cac458843f1da8440ecfe97cf5782d6ca25db5b22ade54ac1cfc3ee25980&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)

6. Select the host that is presented on the printscreen below
![myimage-alt-tag](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/cba9cf8f-61be-4bdf-a5d9-31b0f30d7022/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220619T095806Z&X-Amz-Expires=86400&X-Amz-Signature=871640f442fdcbe3883fcb86bf6f4cc4bdcd6d6c9e0fb7c6e41d637eb7c83597&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)

## Installing the required software in the VM
1. Run this first in your SSH session: `sudo apt update && sudo apt -y upgrade`
    * It's a good idea to run this command often, once per day or every few days, to keep your VM up to date.

### Docker:
1. Run `sudo apt install docker.io` to install it.
1. Change your settings so that you can run Docker without `sudo`:
    1. Run `sudo groupadd docker`
    1. Run `sudo gpasswd -a $USER docker`
    1. Log out of your SSH session and log back in.
    1. Run `sudo service docker restart`
    1. Test that Docker can run successfully with `docker run hello-world`
    2. If you want to test something more useful please try `docker run -it ubuntu bash`

### Docker compose:
1. Go to https://github.com/docker/compose/releases and copy the URL for the  `docker-compose-linux-x86_64` binary for its latest version.
    * At the time of writing, the last available version is `v2.6.0` and the URL for it is https://github.com/docker/compose/releases/download/v2.6.0/docker-compose-linux-x86_64
1. Create a folder for binary files for your Linux user:
    1. Create a subfolder `bin` in your home account with `mkdir ~/bin`
    1. Go to the folder with `cd ~/bin`
1. Download the binary file with `wget <compose_url> -O docker-compose`
    * If you forget to add the `-O` option, you can rename the file with `mv <long_filename> docker-compose`
    * Make sure that the `docker-compose` file is in the folder with `ls`
1. Make the binary executable with `chmod +x docker-compose`
    * Check the file with `ls` again; it should now be colored green. You should now be able to run it with `./docker-compose version`
1. Go back to the home folder with `cd ~`
1. Run `nano .bashrc` to modify your path environment variable:
    1. Scroll to the end of the file
    1. Add this line at the end:
       ```bash
        export PATH="${HOME}/bin:${PATH}"
        ```
    1. Press `CTRL` + `o` in your keyboard and press Enter afterwards to save the file.
    1. Press `CTRL` + `x` in your keyboard to exit the Nano editor.
1. Reload the path environment variable with `source .bashrc`
1. You should now be able to run Docker compose from anywhere; test it with `docker-compose version`

### Terraform:
1. Run `curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -`
1. Run `sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"`
1. Run `sudo apt-get update && sudo apt-get install terraform`

## Upload Google service account credentials file to VM instance

1. Copy the file from local machine using sftp
    1. `sftp de-zoomcamp`
    1. `put google-credentials.json`

## Creating an environment variable for the credentials

Create an environment variable called `GOOGLE_APPLICATION_CREDENTIALS` and assign it to the path of your json credentials file (covered on _Create a Service Account_ section), which should be `$HOME/.google/credentials/` . Assuming you're running bash:

1. Open `.bashrc`:
    ```sh
    nano ~/.bashrc
    ```
1. At the end of the file, add the following line:
    ```sh
    export GOOGLE_APPLICATION_CREDENTIALS="<path/to/authkeys>.json"
    ```
1. Exit nano with `Ctrl+X`. Follow the on-screen instructions to save the file and exit.
1. Log out of your current terminal session and log back in, or run `source ~/.bashrc` to activate the environment variable.
1. Refresh the token and verify the authentication with the GCP SDK:
    ```sh
    gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
    ```
## Clone the repo in the VM

Log in to your VM instance and run the following from your `$HOME` folder:

```sh
git clone https://github.com/FilipeTheAnalyst/DTC-DE-Project.git
```

>***IMPORTANT***: I strongly suggest that you fork my project and clone your copy so that you can easily perform changes on the code, because you will need to customize a few variables in order to make it run with your own infrastructure.

## Set up project infrastructure with Terraform

Make sure that the credentials are updated and the environment variable is set up.

1. Go to the `terraform` folder.

1. Open `variables.tf` and edit line 12 under the `variable "region"` block so that it matches your preferred region.

1. Initialize Terraform:
    ```sh
    terraform init
    ```
1. Plan the infrastructure and make sure that you're creating a bucket in Cloud Storage as well as a dataset in BigQuery
    ```sh
    terraform plan
    ```
1. If the plan details are as expected, apply the changes.
    ```sh
    terraform apply
    ```

You should now have a bucket called `dtc_data_lake_youtube_data` and a dataset called `youtube_data` in BigQuery.

## Set up data ingestion with Airflow

1. Go to the `airflow` folder.
1. Run the following command and write down the output:
    ```sh
    echo -e "AIRFLOW_UID=$(id -u)"
    ```
1. Edit the `.env` file with the following data:
```sh
AIRFLOW_UID=1001
EMAIL_USER=your_email_account
EMAIL_PASSWORD=generated_app_password
```
   Change the value of `AIRFLOW_UID` for the value of the previous command.
   You should change the `EMAIL_USER` to your e-mail user account and for `EMAIL_PASSWORD` you have to create an app-specific password on Gmail. Here is a [tutorial](https://www.lifewire.com/get-a-password-to-access-gmail-by-pop-imap-2-1171882) to support on this step.
1. Open the `docker-compose.yaml` file and change the values of `GCP_PROJECT_ID`, `GCP_GCS_BUCKET` and `BIGQUERY_DATASET` on lines 65-67 for the correct values of your configuration
1. Build the custom Airflow Docker image:
    ```sh
    docker-compose build
    ```
1. Initialize the Airflow configs:
    ```sh
    docker-compose up airflow-init
    ```
1. Run Airflow
    ```sh
    docker-compose up
    ```
1. Although I have inserted on [Dockerfile](https://github.com/FilipeTheAnalyst/DTC-DE-Project/blob/master/airflow/Dockerfile) the python packages needed to run the code inside docker container, I wasn't able to make it work with the Scrapy framework that I used to web scrape data. To achieve that I had to install Scrapy directly on airflow worker performing the following steps:
- Execute `docker ps` on bash to get the containers ids and search for airflow-worker
```sh
    CONTAINER ID   IMAGE                       COMMAND                  CREATED          STATUS                    PORTS                                                 NAMES
fbb212ef7755   airflow_airflow-worker      "/usr/bin/dumb-init ???"   30 minutes ago   Up 30 minutes (healthy)   8080/tcp                                              airflow-airflow-worker-1
e0ad055214fe   airflow_airflow-triggerer   "/usr/bin/dumb-init ???"   30 minutes ago   Up 30 minutes (healthy)   8080/tcp                                              airflow-airflow-triggerer-1
3243e7d76abd   airflow_airflow-webserver   "/usr/bin/dumb-init ???"   30 minutes ago   Up 30 minutes (healthy)   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp             airflow-airflow-webserver-1
342283c1c100   airflow_flower              "/usr/bin/dumb-init ???"   30 minutes ago   Up 30 minutes (healthy)   0.0.0.0:5555->5555/tcp, :::5555->5555/tcp, 8080/tcp   airflow-flower-1
705af99c80fc   airflow_airflow-scheduler   "/usr/bin/dumb-init ???"   30 minutes ago   Up 30 minutes (healthy)   8080/tcp                                              airflow-airflow-scheduler-1
11d1c0202549   redis:latest                "docker-entrypoint.s???"   30 minutes ago   Up 30 minutes (healthy)   6379/tcp                                              airflow-redis-1
bedd33c18f96   postgres:13                 "docker-entrypoint.s???"   30 minutes ago   Up 30 minutes (healthy)   5432/tcp                                              airflow-postgres-1
```
- Execute the following command to access the airflow-worker container bash (using the id obtained on the previous command)
```sh
docker exec -it fbb212ef7755 bash
```
- Run `pip install scrapy` to install the missing python package

You may now access the Airflow GUI by browsing to `localhost:8080`. Username and password are both `airflow` .
>***IMPORTANT***: this is ***NOT*** a production-ready setup! The username and password for Airflow have not been modified in any way; you can find them by searching for `_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD` inside the `docker-compose.yaml` file.
- If you can't connect to Airflow you need to forward 8080 port to your local machine. You can this on VSCode following these steps:
   - Open terminal
   - Click on Ports
   - Select the option Forward a port and select port 8080

![myimage-alt-tag](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/8d928906-e102-4e8f-8378-24bb2c3e6968/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220619%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220619T215750Z&X-Amz-Expires=86400&X-Amz-Signature=ba9282e9fc45f00694a2065d57c392540a4f92b7944281f14089d94eb808cd92&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)

## Perform the data ingestion

If you performed all the steps of the previous section, you should now have a web browser with the Airflow dashboard.

The DAG is set up to download all data starting from 2022-07-18. You may change this date by modifying line 58 of [`airflow/dags/data_ingestion_bgg.py`](https://github.com/FilipeTheAnalyst/DTC-DE-Project/blob/master/airflow/dags/data_ingestion_bgg.py). Should you change the DAG date, you will have to delete the DAG in the Airflow UI and wait a couple of minutes so that Airflow can pick up the changes in the DAG.

To trigger the DAG, simply click on the switch icon next to the DAG name. The DAG will retrieve all data from the boargamegeek website and online stores and check if any of your boardgames inside your [wishlist](https://github.com/FilipeTheAnalyst/DTC-DE-Project/blob/master/airflow/dags/boardgamescraper/boardgames_wishlist.csv) reached your desired price. Feel free to change the records from the `boardgames_wishlist.csv` file to perform tests.

The DAG consists on the following tasks:

![Airflow](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/031a9f47-29d9-4aa9-973d-2ace0fe2a3cb/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220720%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220720T233127Z&X-Amz-Expires=86400&X-Amz-Signature=242711f64c03e5e4a4689849db89eb2ca65cf027882a36f61b9f34494bc749a6&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)

After successfully running the Airflow workflow you should get the following folders and respective parquet files created on GCP bucket for each day:
![gcs_bucket](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/c6c664cb-3176-4eeb-837a-137679a25eee/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220720%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220720T233537Z&X-Amz-Expires=86400&X-Amz-Signature=b5a25a7a3a6461f23532f2c07ffa1cd60780976135ece027bd58f07f91c3be46&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)

And the tables boardgames and gamesprices created inside capstone_boardgame_data dataset:
![gcp_bq](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/2959536f-0180-4a03-878e-686ac271acc3/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220720%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220720T233810Z&X-Amz-Expires=86400&X-Amz-Signature=0637019635dfec5c756d184404c6c42b453f4d88672d65e91b7d6898fd21d88c&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)


After the data ingestion, you may shut down Airflow by pressing `Ctrl+C` on the terminal running Airflow and then running `docker-compose down`, or you may keep Airflow running if you want to update the dataset every day.

### Example of price alert notification via e-mail
If any boardgame present on your wishlist reached a target price below the desired value, you'll receive an email like this one below.
![price_alert](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/73fbd110-434c-4bda-8a1f-4e608172922e/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220721%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220721T004858Z&X-Amz-Expires=86400&X-Amz-Signature=63cce2277e812698e0d5e9dea45aef4992a362fe1ad3219def2bf27dba59459d&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)

## Data transformation with DBT
I created a table in BigQuery using DBT to consolidate the data from boardgames and gamesprices tables.
The [dbt models are presented here](https://github.com/FilipeTheAnalyst/DTC-DE-Project/tree/master/dbt_project/models).

Just need to import the data inside the [dbt_project folder](https://github.com/FilipeTheAnalyst/DTC-DE-Project/tree/master/dbt_project) and use the models from core and staging folders as well as the macro.

Then you just need to run `dbt run` to execute all the dependencies needed to created the tables defined as shown below.

![dbt_lineage](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/0d0f55de-f6eb-4cb5-9ceb-da934fef0057/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220721%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220721T113607Z&X-Amz-Expires=86400&X-Amz-Signature=8fee395a37b490efce166be37d534be8fe63f23645ef093ed0d4ec74da9be0e3&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22Untitled.png%22&x-id=GetObject)

## Data visualization with Google Data Studio
The dashboards are available [in this link](https://datastudio.google.com/reporting/3f21fa08-66b2-4b85-bcf6-69711ecc73b9).
As an alternative I also converted to a pdf file available on this [repo](https://github.com/FilipeTheAnalyst/DTC-DE-Project/blob/master/Boardgames_Analysis.pdf).

