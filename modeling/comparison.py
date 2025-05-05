"""Simplified Transcript Summarizer Comparison Tool

This script creates a focused visual comparison between two summarizer systems.

Usage:
     comparison.py --summaries1 <path_to_system1_summaries>
                   --summaries2 <path_to_system2_summaries>
                   [--output_dir <output_directory>]
"""

import os
import argparse
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm
from rouge_score import rouge_scorer
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def load_summaries(dir_path):
    """Load summaries from a directory with robust error handling"""
    summaries = {}
    try:
        files = list(Path(dir_path).glob("*.txt"))
        if not files:
            print(f"Warning: No .txt files found in {dir_path}")
            return summaries
            
        for file_path in tqdm(files, desc=f"Loading from {dir_path}"):
            file_id = file_path.stem
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                    # Extract just the summary if it follows a pattern like "Summary: [content]"
                    summary_match = re.search(r"Summary:\s*(.*?)(?:\n\n|\Z)", text, re.DOTALL)
                    if summary_match:
                        summaries[file_id] = summary_match.group(1).strip()
                    else:
                        summaries[file_id] = text
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
    except Exception as e:
        print(f"Error accessing directory {dir_path}: {e}")
    
    return summaries

def create_comparison_radar_chart(system1_summaries, system2_summaries, output_path):
    """Create a single radar chart comparing the two systems"""
    # Initialize metrics
    rouge_scorer_obj = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    # Find common file IDs
    common_ids = set(system1_summaries.keys()) & set(system2_summaries.keys())
    print(f"Found {len(common_ids)} common transcripts between both systems.")
    
    if len(common_ids) == 0:
        print("Error: No common files found between the two systems.")
        return None
    
    # Calculate metrics for each file
    metrics = {
        "word_count": {"System 1": [], "System 2": []},
        "sentence_count": {"System 1": [], "System 2": []},
        "vocabulary_richness": {"System 1": [], "System 2": []},
        "rouge1_f": [],
        "rouge2_f": [],
        "rougeL_f": [],
        "semantic_similarity": []
    }
    
    for file_id in tqdm(common_ids, desc="Calculating metrics"):
        summary1 = system1_summaries[file_id]
        summary2 = system2_summaries[file_id]
        
        # Skip empty summaries
        if not summary1 or not summary2:
            print(f"Warning: Empty summary found for {file_id}, skipping.")
            continue
        
        # Calculate basic metrics
        metrics["word_count"]["System 1"].append(len(summary1.split()))
        metrics["word_count"]["System 2"].append(len(summary2.split()))
        
        metrics["sentence_count"]["System 1"].append(len(sent_tokenize(summary1)))
        metrics["sentence_count"]["System 2"].append(len(sent_tokenize(summary2)))
        
        # Vocabulary richness
        tokens1 = word_tokenize(summary1.lower())
        tokens2 = word_tokenize(summary2.lower())
        
        if tokens1:
            metrics["vocabulary_richness"]["System 1"].append(len(set(tokens1)) / len(tokens1))
        else:
            metrics["vocabulary_richness"]["System 1"].append(0)
            
        if tokens2:
            metrics["vocabulary_richness"]["System 2"].append(len(set(tokens2)) / len(tokens2))
        else:
            metrics["vocabulary_richness"]["System 2"].append(0)
        
        # ROUGE scores
        try:
            rouge_scores = rouge_scorer_obj.score(summary1, summary2)
            metrics["rouge1_f"].append(rouge_scores["rouge1"].fmeasure)
            metrics["rouge2_f"].append(rouge_scores["rouge2"].fmeasure)
            metrics["rougeL_f"].append(rouge_scores["rougeL"].fmeasure)
        except Exception as e:
            print(f"Error calculating ROUGE scores for {file_id}: {e}")
            metrics["rouge1_f"].append(0)
            metrics["rouge2_f"].append(0)
            metrics["rougeL_f"].append(0)
        
        # Semantic similarity
        try:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([summary1, summary2])
            metrics["semantic_similarity"].append(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        except Exception as e:
            print(f"Error calculating semantic similarity for {file_id}: {e}")
            metrics["semantic_similarity"].append(0)
    
    # Check if we have any valid metrics
    if not metrics["word_count"]["System 1"]:
        print("Error: No valid metrics could be calculated after filtering empty summaries.")
        return None
    
    # Calculate means for each metric
    summary = {
        "word_count": {
            "System 1": np.mean(metrics["word_count"]["System 1"]),
            "System 2": np.mean(metrics["word_count"]["System 2"])
        },
        "sentence_count": {
            "System 1": np.mean(metrics["sentence_count"]["System 1"]),
            "System 2": np.mean(metrics["sentence_count"]["System 2"])
        },
        "vocabulary_richness": {
            "System 1": np.mean(metrics["vocabulary_richness"]["System 1"]),
            "System 2": np.mean(metrics["vocabulary_richness"]["System 2"])
        },
        "rouge1_f": np.mean(metrics["rouge1_f"]),
        "rouge2_f": np.mean(metrics["rouge2_f"]),
        "rougeL_f": np.mean(metrics["rougeL_f"]),
        "semantic_similarity": np.mean(metrics["semantic_similarity"])
    }
    
    # Create radar chart
    categories = [
        "Word Count", 
        "Sentence Count",
        "Vocabulary Richness", 
        "ROUGE-1",
        "ROUGE-2",
        "ROUGE-L",
        "Semantic Similarity"
    ]
    
    # Normalize values for radar chart with reasonable caps
    max_word_count = max(summary["word_count"]["System 1"], summary["word_count"]["System 2"])
    max_word_count = min(max_word_count, 500)  # Cap at reasonable maximum
    
    max_sentence_count = max(summary["sentence_count"]["System 1"], summary["sentence_count"]["System 2"])
    max_sentence_count = min(max_sentence_count, 30)  # Cap at reasonable maximum
    
    # Get values for System 1
    system1_values = [
        min(summary["word_count"]["System 1"] / max_word_count, 1.0),
        min(summary["sentence_count"]["System 1"] / max_sentence_count, 1.0),
        summary["vocabulary_richness"]["System 1"],
        summary["rouge1_f"],
        summary["rouge2_f"],
        summary["rougeL_f"],
        summary["semantic_similarity"]
    ]
    
    # Get values for System 2
    system2_values = [
        min(summary["word_count"]["System 2"] / max_word_count, 1.0),
        min(summary["sentence_count"]["System 2"] / max_sentence_count, 1.0),
        summary["vocabulary_richness"]["System 2"],
        summary["rouge1_f"],
        summary["rouge2_f"],
        summary["rougeL_f"],
        summary["semantic_similarity"]
    ]
    
    # Ensure values are in range [0,1] for radar chart
    system1_values = [min(max(0, v), 1) for v in system1_values]
    system2_values = [min(max(0, v), 1) for v in system2_values]
    
    # Number of variables
    N = len(categories)
    
    # Create angles for each metric
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop
    
    # Add values for the loop closure
    system1_values += system1_values[:1]
    system2_values += system2_values[:1]
    
    # Create radar chart
    plt.figure(figsize=(14, 12))
    ax = plt.subplot(111, polar=True)
    
    # Plot System 1
    ax.plot(angles, system1_values, 'o-', linewidth=2, label="System 1", color="#3498db")
    ax.fill(angles, system1_values, alpha=0.25, color="#3498db")
    
    # Plot System 2
    ax.plot(angles, system2_values, 'o-', linewidth=2, label="System 2", color="#e74c3c")
    ax.fill(angles, system2_values, alpha=0.25, color="#e74c3c")
    
    # Set labels and formatting
    plt.xticks(angles[:-1], categories, size=14)
    
    # Improve label positioning to avoid overlap
    for label, angle in zip(ax.get_xticklabels(), angles[:-1]):
        if angle < np.pi/2 or angle > 3*np.pi/2:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')
    
    ax.set_title("Transcript Summarizer Comparison", size=20, pad=20)
    
    # Add axis labels with actual values
    for i, angle in enumerate(angles[:-1]):
        if i == 0:  # Word count
            ax.text(angle, 1.1, f"Max: {int(max_word_count)} words", 
                   ha='center', va='center', size=10)
        elif i == 1:  # Sentence count
            ax.text(angle, 1.1, f"Max: {int(max_sentence_count)} sentences", 
                   ha='center', va='center', size=10)
    
    # Add legend with metrics
    legend = plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))
    
    # Add a text box with key statistics
    textstr = '\n'.join((
        f"Word Count: System 1 = {int(summary['word_count']['System 1'])}, System 2 = {int(summary['word_count']['System 2'])}",
        f"Sentence Count: System 1 = {summary['sentence_count']['System 1']:.1f}, System 2 = {summary['sentence_count']['System 2']:.1f}",
        f"Vocabulary Richness: System 1 = {summary['vocabulary_richness']['System 1']:.3f}, System 2 = {summary['vocabulary_richness']['System 2']:.3f}",
        f"Semantic Similarity: {summary['semantic_similarity']:.3f}",
        f"ROUGE-1: {summary['rouge1_f']:.3f}",
        f"ROUGE-2: {summary['rouge2_f']:.3f}",
        f"ROUGE-L: {summary['rougeL_f']:.3f}"
    ))
    
    # Create a text box at the bottom
    plt.figtext(0.5, 0.01, textstr, ha="center", fontsize=12, 
                bbox={"facecolor":"white", "alpha":0.8, "pad":5, "boxstyle":"round,pad=0.5"})
    
    plt.tight_layout()
    
    # Save the visualization
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Radar chart saved to {output_path}")
    except Exception as e:
        print(f"Error saving radar chart: {e}")
    finally:
        plt.close()
    
    return summary

def main():
    parser = argparse.ArgumentParser(description="Compare two summarizer systems with a single visualization")
    parser.add_argument("--summaries1", required=True, help="Directory containing summaries from system 1")
    parser.add_argument("--summaries2", required=True, help="Directory containing summaries from system 2")
    parser.add_argument("--output_dir", default="./comparison_results", help="Directory to save comparison results")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Load summaries
    print("Loading summaries...")
    system1_summaries = load_summaries(args.summaries1)
    system2_summaries = load_summaries(args.summaries2)
    
    if not system1_summaries:
        print(f"Error: No valid summaries found in {args.summaries1}")
        return
    
    if not system2_summaries:
        print(f"Error: No valid summaries found in {args.summaries2}")
        return
    
    # Create the comparison chart
    print("Creating comparison visualization...")
    summary = create_comparison_radar_chart(
        system1_summaries, 
        system2_summaries, 
        output_dir / "summarizer_comparison_radar.png"
    )
    
    if summary:
        # Save the summary data
        try:
            with open(output_dir / "comparison_summary.json", "w") as f:
                json.dump(summary, f, indent=2)
            print(f"Comparison complete! Results saved to {output_dir}")
        except Exception as e:
            print(f"Error saving summary data: {e}")
    else:
        print("Comparison failed. Please check the error messages above.")

if __name__ == "__main__":
    main()