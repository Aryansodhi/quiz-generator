# test_qg_flan.py

from utils.qg_flan import generate_mcq_flan

sample = (
    "Photosynthesis is the process by which green plants use sunlight "
    "to synthesize food from carbon dioxide and water. It occurs in chloroplasts."
)

# generate_mcq_flan(sample, num_questions=3)
generate_mcq_flan("E:/Documents/cs203/DLD_Report.pdf", num_questions=6)