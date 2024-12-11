import cv2
from final_version import *


frame = cv2.imread('imgpsh_fullsize_anim.png')

processed_image = preprocess_image(frame)
text_regions = find_text_regions(np.ones(processed_image.shape, dtype=np.uint8)*255 - processed_image)
extracted_text = extract_text_from_regions(processed_image, text_regions)
print(extracted_text)
if extracted_text:
    extracted_text_clean = ' '.join(extracted_text.split())
    
    best_match, match_score = process.extractOne(
        extracted_text_clean,
        questions,
        scorer=fuzz.partial_ratio
    )
    
    if match_score > 80:  # Match threshold
        answer = next((row[1] for row in quizzes_data if row[0] == best_match), None)
        result = f"Question: {best_match}\nAnswer: {answer}\nMatch Score: {match_score}"
        if answer is 'V':
            vibrate(2)
        else:
            vibrate(1)
    else:
        result = f"No match found. Best match score: {match_score}"
print(result)