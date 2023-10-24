# Rated API Setup and Usage

## How to Run It

### 1. Clone the Repository

`git clone https://github.com/raresmihai/rated-api.git`  

### 2. Set Up a Virtual Environment
```bash
cd rated-api
python -m venv venv  
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Server
`python -m server.main --process_csv`

Note: If it's not the first time you process the csv and you already have the `ratedapi.db` file populated, you don't need to pass `--process_csv`. 
Doing so will re-run the processing but fail to insert due to duplicated rows. You'll get the following log:

```[SqlRepository] Duplicate transaction detected with hash 0x1d9dfb42e09e93271fd09bd43c6fb349e81e42668686469d6450283812ff884f```

### 4. Sample API Calls:
`curl -X GET http://127.0.0.1:8000/stats`

Expected Response:
```json
{
  "totalTransactionsInDB": 5000,
  "totalGasUsed": 494112901,
  "totalGasCostInDollars": 19211.87
}
```

`curl -X GET http://127.0.0.1:8000/transactions/0xc055b65e39c15e1bc90cb4ccb2daac6b59c02ec1aa6c4216276054b4f31ed90a`

```json
Expected Response:
{
    "hash":"0xc055b65e39c15e1bc90cb4ccb2daac6b59c02ec1aa6c4216276054b4f31ed90a",
    "fromAddress":"0xd5e87f1f003f222188cc8c5aeefc8b285738b7e7",
    "toAddress":"0xf24a5cc235e5242d69fafbffd304f63b92ac82f9",
    "blockNumber":17818542,
    "executedAt":"2023-08-01T07:04:59",
    "gasUsed":295582,
    "gasCostInDollars":12.87
}
```

### 5. Run the Tests
`pytest tests/`

## Solution

[https://github.com/rated-network/coding-challenge](https://github.com/rated-network/coding-challenge)

Here are the detailed steps followed in the solution:

*1. Assuming block length is 12 seconds, compute the approximate execution timestamp of each transaction.*
- The `block_timestamp` is set as the transaction timestamp.

*2. Compute the gas cost of each transaction in Gwei (1e-9 ETH).*
```plaintext
gas_cost_wei = transaction.receipts_gas_used * transaction.receipts_effective_gas_price
gas_cost_gwei = gas_cost_wei / 1e9
```

*3. Using Coingecko's API, retrieve the approximate price of ETH at transaction execution time and compute the dollar cost of gas used.*
- Approximate price is considered as the last known price before the transaction timestamp. Depending on the age of the transaction and the granularity of the CoinGecko API, this can be up to 5 minutes, 1 hour, or 1 day before the actual transaction time.

*4. Populate a local database with the processed transactions.*
- A local SqlLite in-memory file database is used. The database can be easily switched to a different one using the database config.

*5. Using the database in part 4, implement an API endpoint in a framework of your choosing that serves the following endpoints*
- The APIs are exposed using FastAPI, and the models are implemented with pydantic.

## TO DO

Below is a list of some tasks and improvements that would be necessary for a production-like environment:

### Validation and Error Handling

- Some minimal model validation is already implemented using pydantic. For a production environment, we would:
    - Add more comprehensive API validation.
    - Implement robust exception handling. Currently, if an API endpoint throws an exception, a 500 status will be returned.
    - It's essential to catch different exceptions that might arise, log them, emit relevant metrics, and implement alerts.
    - Additional unit tests, especially for database and server packages, are required.

### Authentication

- At present, the APIs are public. In a production-like environment:
    - We'd implement an authentication mechanism, potentially through API keys or tokens.
    - It would be advisable to implement a rate limiter, akin to the one used by the Coingecko API.

### AWS Resources

- The project currently utilizes a local server and an in-memory database. For production:
    - We'd transition to resources on a remote server or, preferably, a cloud provider like AWS.
    - Potential AWS resources based on functional and non-functional requirements include:
        1. A WebServer on an EC2 instance, a Kubernetes cluster, or even a serverless Lambda function.
        2. An RDS database utilizing engines such as MySql, PostgreSQL, or MariaDB.
        3. A message broker like Kafka or a combination of SQS and SNS for processing transactions in a streaming manner.
        4. Additional infrastructure like gateways, load balancers, IAM roles, etc.

### Infrastructure as Code

- After defining the cloud resources:
    - Tools like Terraform or AWS CDK could be employed to encapsulate the infrastructure as code.
    - This facilitates setting up CI/CD pipelines and environments.

### Monitoring

- Currently, logs are simply printed to the console. In a production setup:
    - We'd adopt a managed monitoring and telemetry solution, exploring options such as CloudWatch, Kibana combined with Grafana, Datadog, and more.
