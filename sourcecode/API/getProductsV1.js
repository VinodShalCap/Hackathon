import { DynamoDBClient, ScanCommand } from "@aws-sdk/client-dynamodb";
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { unmarshall } from "@aws-sdk/util-dynamodb";
import { Readable } from "stream";

const client = new DynamoDBClient({ region: process.env.AWS_REGION });
const s3Client = new S3Client({ region: process.env.AWS_REGION });

const bucketName = "team-genai-innovators-common";
const fileName = "generaged_data/generatedData.json";

export const handler = async (event) => {
  const params = {
    TableName: "team-genai-innovators-cca-products",
  };

  try {
    const paramsS3 = {
      Bucket: bucketName,
      Key: fileName,
    };

    const { Body } = await s3Client.send(new GetObjectCommand(paramsS3));
    const responseBody = await streamToString(Body);
    const additionalDataMapping = JSON.parse(responseBody);

    const data = await client.send(new ScanCommand(params));
    const jsonItems = data.Items.map((item) => {
      const plainItem = unmarshall(item);
      const additionalData = additionalDataMapping[plainItem.pk] || { discount: "0", proposed_price: "0", competator_price: "0" };
      return { ...plainItem, ...additionalData };
    });

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
      },
      body: (jsonItems),
    };
  } catch (err) {
    console.error("Error:", err);
    return {
      statusCode: 500,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ error: err.message }),
    };
  }
};

const streamToString = (stream) =>
  new Promise((resolve, reject) => {
    const chunks = [];
    stream.on("data", (chunk) => chunks.push(chunk));
    stream.on("error", reject);
    stream.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
  });
