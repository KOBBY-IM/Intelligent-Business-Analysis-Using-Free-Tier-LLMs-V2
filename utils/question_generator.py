"""
Module for generating evaluation questions based on available data in the RAG pipeline.
"""
import pandas as pd
import json
from typing import List, Dict, Any

class QuestionGenerator:
    """Generate business analysis questions based on available dataset content."""
    
    def __init__(self):
        pass
    
    def analyze_dataset_structure(self, dataset_path: str) -> Dict[str, Any]:
        """
        Analyze the structure and content of a dataset to understand available data.
        
        Args:
            dataset_path: Path to the dataset file
            
        Returns:
            Dictionary containing dataset analysis
        """
        try:
            # Load the dataset
            df = pd.read_csv(dataset_path)
            
            analysis = {
                'columns': list(df.columns),
                'total_rows': len(df),
                'data_types': df.dtypes.to_dict(),
                'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
                'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
                'date_columns': [],
                'unique_values': {},
                'summary_stats': {}
            }
            
            # Identify date columns
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    analysis['date_columns'].append(col)
                elif df[col].dtype == 'object':
                    # Check if it's a date column by trying to parse
                    try:
                        pd.to_datetime(df[col].iloc[0])
                        analysis['date_columns'].append(col)
                    except:
                        pass
            
            # Get unique values for categorical columns
            for col in analysis['categorical_columns']:
                if col not in analysis['date_columns']:
                    analysis['unique_values'][col] = df[col].nunique()
            
            # Get summary statistics for numeric columns
            if analysis['numeric_columns']:
                analysis['summary_stats'] = df[analysis['numeric_columns']].describe().to_dict()
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing dataset {dataset_path}: {e}")
            return {}
    
    def generate_retail_questions(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate retail-specific questions based on dataset analysis.
        
        Args:
            analysis: Dataset analysis dictionary
            
        Returns:
            List of generated questions
        """
        questions = []
        
        # Check for common retail columns
        has_category = any('category' in col.lower() for col in analysis.get('columns', []))
        has_amount = any('amount' in col.lower() or 'price' in col.lower() or 'sales' in col.lower() for col in analysis.get('columns', []))
        has_location = any('location' in col.lower() or 'region' in col.lower() for col in analysis.get('columns', []))
        has_item = any('item' in col.lower() or 'product' in col.lower() for col in analysis.get('columns', []))
        has_customer = any('customer' in col.lower() or 'age' in col.lower() or 'gender' in col.lower() for col in analysis.get('columns', []))
        
        # Generate questions based on available data
        if has_category and has_amount:
            questions.extend([
                "Which product category generates the highest total revenue?",
                "What is the average transaction value per category?",
                "Which category has the most transactions?",
                "How does revenue distribution vary across product categories?"
            ])
        
        if has_location and has_amount:
            questions.extend([
                "Which region or location generates the highest revenue?",
                "What is the average transaction value by region?",
                "How do sales patterns differ across different locations?",
                "Which region has the most consistent sales performance?"
            ])
        
        if has_item and has_amount:
            questions.extend([
                "What are the top 5 best-selling products by revenue?",
                "Which products have the highest average transaction value?",
                "Are there any products that consistently underperform?",
                "What is the sales distribution for the most popular products?"
            ])
        
        if has_customer and has_amount:
            questions.extend([
                "How do sales patterns differ across customer demographics?",
                "Which customer segment generates the highest revenue?",
                "What is the average transaction value by customer age group?",
                "How do purchasing patterns vary by gender?"
            ])
        
        # Add general business insights questions
        questions.extend([
            "What are the key trends in the sales data?",
            "Which factors most strongly correlate with high-value transactions?",
            "What insights can be drawn about customer purchasing behavior?",
            "How can this data inform inventory management decisions?"
        ])
        
        return questions[:10]  # Return top 10 questions
    
    def generate_finance_questions(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate finance-specific questions based on dataset analysis.
        
        Args:
            analysis: Dataset analysis dictionary
            
        Returns:
            List of generated questions
        """
        questions = []
        
        # Check for common finance columns
        has_date = len(analysis.get('date_columns', [])) > 0
        has_open = any('open' in col.lower() for col in analysis.get('columns', []))
        has_close = any('close' in col.lower() for col in analysis.get('columns', []))
        has_high = any('high' in col.lower() for col in analysis.get('columns', []))
        has_low = any('low' in col.lower() for col in analysis.get('columns', []))
        has_volume = any('volume' in col.lower() for col in analysis.get('columns', []))
        
        # Generate questions based on available data
        if has_date and has_close:
            questions.extend([
                "What is the overall price trend over the time period?",
                "On which date did the stock reach its highest closing price?",
                "What is the average daily price change?",
                "How many days did the stock close higher than it opened?"
            ])
        
        if has_open and has_close:
            questions.extend([
                "What is the correlation between opening and closing prices?",
                "What is the average daily price volatility (high-low range)?",
                "Which days had the largest price swings?",
                "How does the opening price trend compare to the closing price trend?"
            ])
        
        if has_volume:
            questions.extend([
                "What is the average daily trading volume?",
                "Are there any days with unusually high trading volume?",
                "What is the correlation between trading volume and price movement?",
                "Which days had the highest and lowest trading activity?"
            ])
        
        if has_high and has_low:
            questions.extend([
                "What is the average daily trading range?",
                "Which days had the widest price ranges?",
                "How does volatility change over time?",
                "What are the patterns in daily high and low prices?"
            ])
        
        # Add general market analysis questions
        questions.extend([
            "What are the key market trends evident in this data?",
            "How can this data inform investment decisions?",
            "What insights can be drawn about market sentiment?",
            "What are the risk factors indicated by this price data?"
        ])
        
        return questions[:10]  # Return top 10 questions
    
    def generate_questions_from_data(self) -> Dict[str, List[str]]:
        """
        Generate questions for both retail and finance datasets based on actual data.
        
        Returns:
            Dictionary with industry-specific questions
        """
        questions = {}
        
        # Generate retail questions
        try:
            retail_analysis = self.analyze_dataset_structure('data/shopping_trends_with_rag.csv')
            if retail_analysis:
                questions['retail'] = self.generate_retail_questions(retail_analysis)
                print(f"Generated {len(questions['retail'])} retail questions based on data structure")
            else:
                questions['retail'] = []
        except Exception as e:
            print(f"Error generating retail questions: {e}")
            questions['retail'] = []
        
        # Generate finance questions
        try:
            finance_analysis = self.analyze_dataset_structure('data/Tesla_stock_data_with_rag.csv')
            if finance_analysis:
                questions['finance'] = self.generate_finance_questions(finance_analysis)
                print(f"Generated {len(questions['finance'])} finance questions based on data structure")
            else:
                questions['finance'] = []
        except Exception as e:
            print(f"Error generating finance questions: {e}")
            questions['finance'] = []
        
        return questions
    
    def save_questions(self, questions: Dict[str, List[str]], output_path: str = 'data/eval_questions.json'):
        """
        Save generated questions to JSON file.
        
        Args:
            questions: Dictionary of questions by industry
            output_path: Path to save the questions
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(questions, f, indent=2)
            print(f"Questions saved to {output_path}")
        except Exception as e:
            print(f"Error saving questions: {e}")

def main():
    """Generate questions based on available data and save them."""
    generator = QuestionGenerator()
    questions = generator.generate_questions_from_data()
    generator.save_questions(questions)
    
    # Print summary
    print("\nGenerated Questions Summary:")
    for industry, question_list in questions.items():
        print(f"\n{industry.upper()} ({len(question_list)} questions):")
        for i, question in enumerate(question_list, 1):
            print(f"  {i}. {question}")

if __name__ == "__main__":
    main() 