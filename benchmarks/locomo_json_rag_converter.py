import argparse
import json


def main(dataset_path: str, output_path: str):
    with open(file=dataset_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)
    
    sample = data[1] # Choose the second QA task
    sample_id = sample["sample_id"]
    qa = sample["qa"]
    conversation = sample["conversation"]
    
    # Flatten the conversation by merging the sessions
    conversation_flat = []
    session_index = 1
    while True:
        session_name = f"session_{session_index}"
        # Break if there are no more sessions
        if session_name not in conversation:
            break
        
        timestamp = conversation[f"{session_name}_date_time"]
        session = conversation[session_name]

        # Iterate over messages
        for msg in session:
            # Create message item
            msg_item = {
                "id": msg["dia_id"],
                "timestamp": timestamp,
                "speaker": msg["speaker"],
                "text": msg["text"],
            }

            # Include blib caption if present
            blip_caption = msg.get("blip_caption")
            if blip_caption is not None:
                msg_item["blip_caption"] = blip_caption

            # Append the message
            conversation_flat.append(msg_item)

        session_index += 1

    # Skip adversarial questions
    qa_no_adversarial = [item for item in qa if item["category"] != 5]

    result = {
        sample_id: {
            "conversation": conversation_flat,
            "question": qa_no_adversarial,
        }
    }

    with open(file=output_path, mode="w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dataset-path",
        type=str,
        default="data/locomo/locomo10.json",
        help="Path to locomo benchmark json file",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="data/locomo/locomo10_rag_with_metadata.json",
        help="Path to the output file to store the converted json",
    )
    args = parser.parse_args()

    main(
        dataset_path=args.dataset_path,
        output_path=args.output_path,
    )
