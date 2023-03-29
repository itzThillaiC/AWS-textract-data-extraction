
import boto3
import io
from PIL import Image, ImageDraw

def draw_bounding_box(key, val, width, height, draw):
    # If a key is Geometry, draw the bounding box info in it
    if "Geometry" in key:
        # Draw bounding box information
        box = val["BoundingBox"]
        left = width * box['Left']
        top = height * box['Top']
        draw.rectangle([left, top, left + (width * box['Width']), top + (height * box['Height'])],
                       outline='black')

# Takes a field as an argument and prints out the detected labels and values
def print_labels_and_values(field):
    # Initialize sets to keep track of which values have already been printed
    label_values = set()
    value_values = set()

    # Check if LabelDetection key exists
    if "LabelDetection" in field:
        # Get label detection text value
        label_value = str(field["LabelDetection"].get("Text", "")).strip()

        # Check if label value has already been printed
        if label_value not in label_values:
            print("Summary Label Detection - Confidence: {}, Summary Values: {}".format(
                str(field["LabelDetection"].get("Confidence", "")), label_value))
            # Add label value to printed set
            label_values.add(label_value)
        else:
            print("Repeated Summary Label Detection - Skipping")

    else:
        print("Label Detection - No labels returned.")
    
    # Check if ValueDetection key exists
    if "ValueDetection" in field:
        # Get value detection text value
        value_value = str(field["ValueDetection"].get("Text", "")).strip()

        # Check if value value has already been printed
        if value_value not in value_values:
            print("Summary Value Detection - Confidence: {}, Summary Values: {}".format(
                str(field["ValueDetection"].get("Confidence", "")), value_value))
            # Add value value to printed set
            value_values.add(value_value)
        else:
            print("Repeated Summary Value Detection - Skipping")

    else:
        print("Value Detection - No values returned.")




def process_expense_analysis(s3_connection, client, bucket, document):
        
    # Get the document from S3
    s3_object = s3_connection.Object(bucket, document)
    s3_response = s3_object.get()

    # opening binary stream using an in-memory bytes buffer
    stream = io.BytesIO(s3_response['Body'].read())

    # loading stream into image
    image = Image.open(stream)

    # Analyze document
    # process using S3 object
    response = client.analyze_expense(
        Document={'S3Object': {'Bucket': bucket, 'Name': document}})

    # Set width and height to display image and draw bounding boxes
    # Create drawing object
    width, height = image.size
    draw = ImageDraw.Draw(image)

    for expense_doc in response["ExpenseDocuments"]:
        for line_item_group in expense_doc["LineItemGroups"]:
            for line_items in line_item_group["LineItems"]:
                for expense_fields in line_items["LineItemExpenseFields"]:
                    print_labels_and_values(expense_fields)
                    print()

        print("Summary:")
        for summary_field in expense_doc["SummaryFields"]:
            print_labels_and_values(summary_field)
            print()

        #For draw bounding boxes
        for line_item_group in expense_doc["LineItemGroups"]:
            for line_items in line_item_group["LineItems"]:
                for expense_fields in line_items["LineItemExpenseFields"]:
                    for key, val in expense_fields["ValueDetection"].items():
                        if "Geometry" in key:
                            draw_bounding_box(key, val, width, height, draw)

        for label in expense_doc["SummaryFields"]:
            if "LabelDetection" in label:
                for key, val in label["LabelDetection"].items():
                    draw_bounding_box(key, val, width, height, draw)

    # Display the image
    image.show()

def main():
    session = boto3.Session(profile_name='billok')
    s3_connection = session.resource('s3')
    client = session.client('textract', region_name='us-east-1')
    bucket = 'billfly-bucket'
    document = 'invoice_1.jpg'
    process_expense_analysis(s3_connection, client, bucket, document)

if __name__ == "__main__":
    main()