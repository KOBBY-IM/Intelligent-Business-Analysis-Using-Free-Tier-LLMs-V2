#!/usr/bin/env python3
"""
Comprehensive analysis of the LLM evaluation data
"""

import pandas as pd
import numpy as np

def analyze_data():
    print("🔍 COMPREHENSIVE LLM EVALUATION ANALYSIS")
    print("=" * 60)
    
    # Load data
    df = pd.read_csv('data/batch_eval_metrics.csv')
    
    print(f"\n📊 DATASET OVERVIEW:")
    print(f"   Total Records: {len(df):,}")
    print(f"   Time Period: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"   Providers: {', '.join(df['llm_provider'].unique())}")
    print(f"   Models: {len(df['llm_model'].unique())} models")
    print(f"   Industries: {', '.join(df['industry'].unique())}")
    
    print(f"\n🎯 KEY METRICS:")
    print(f"   Overall Success Rate: {(df['success'].sum() / len(df)) * 100:.2f}%")
    print(f"   Average Latency: {df['latency_sec'].mean():.2f}s")
    print(f"   Average Throughput: {df['throughput_tps'].mean():.2f} tokens/sec")
    print(f"   Total Tokens Processed: {df['total_tokens'].sum():,}")
    
    print(f"\n🏆 PROVIDER PERFORMANCE COMPARISON:")
    provider_stats = df.groupby('llm_provider').agg({
        'latency_sec': ['mean', 'std', 'min', 'max'],
        'throughput_tps': ['mean', 'std'],
        'success': 'mean',
        'total_tokens': 'mean',
        'retry_count': 'mean'
    }).round(2)
    
    for provider in df['llm_provider'].unique():
        provider_data = df[df['llm_provider'] == provider]
        success_rate = (provider_data['success'].sum() / len(provider_data)) * 100
        avg_latency = provider_data['latency_sec'].mean()
        avg_throughput = provider_data['throughput_tps'].mean()
        
        print(f"\n   {provider.upper()}:")
        print(f"     Success Rate: {success_rate:.2f}%")
        print(f"     Avg Latency: {avg_latency:.2f}s")
        print(f"     Avg Throughput: {avg_throughput:.2f} tokens/sec")
        print(f"     Avg Tokens: {provider_data['total_tokens'].mean():.0f}")
        print(f"     Avg Retries: {provider_data['retry_count'].mean():.2f}")
    
    print(f"\n🤖 MODEL PERFORMANCE BREAKDOWN:")
    model_stats = df.groupby(['llm_provider', 'llm_model']).agg({
        'latency_sec': 'mean',
        'throughput_tps': 'mean',
        'success': 'mean',
        'total_tokens': 'mean'
    }).round(2)
    
    for (provider, model), stats in model_stats.iterrows():
        success_rate = stats['success'] * 100
        print(f"\n   {provider.upper()} - {model}:")
        print(f"     Success Rate: {success_rate:.2f}%")
        print(f"     Avg Latency: {stats['latency_sec']:.2f}s")
        print(f"     Avg Throughput: {stats['throughput_tps']:.2f} tokens/sec")
        print(f"     Avg Tokens: {stats['total_tokens']:.0f}")
    
    print(f"\n💼 INDUSTRY PERFORMANCE:")
    industry_stats = df.groupby('industry').agg({
        'latency_sec': 'mean',
        'throughput_tps': 'mean',
        'success': 'mean'
    }).round(2)
    
    for industry, stats in industry_stats.iterrows():
        success_rate = stats['success'] * 100
        print(f"\n   {industry.upper()}:")
        print(f"     Success Rate: {success_rate:.2f}%")
        print(f"     Avg Latency: {stats['latency_sec']:.2f}s")
        print(f"     Avg Throughput: {stats['throughput_tps']:.2f} tokens/sec")
    
    print(f"\n🚨 ERROR ANALYSIS:")
    failures = df[df['success'] == False]
    total_failures = len(failures)
    
    if total_failures > 0:
        print(f"   Total Failures: {total_failures}")
        print(f"   Failure Rate: {(total_failures / len(df)) * 100:.2f}%")
        
        # Error types
        if 'error_type' in failures.columns:
            error_types = failures['error_type'].value_counts()
            print(f"\n   Error Types:")
            for error_type, count in error_types.items():
                percentage = (count / total_failures) * 100
                print(f"     {error_type}: {count} ({percentage:.1f}%)")
        
        # Provider failure comparison
        print(f"\n   Provider Failure Rates:")
        for provider in df['llm_provider'].unique():
            provider_data = df[df['llm_provider'] == provider]
            provider_failures = len(provider_data[provider_data['success'] == False])
            failure_rate = (provider_failures / len(provider_data)) * 100
            print(f"     {provider.upper()}: {failure_rate:.2f}% ({provider_failures} failures)")
    else:
        print("   No failures recorded in the dataset")
    
    print(f"\n📈 PERFORMANCE INSIGHTS:")
    
    # Best performing model
    best_model = model_stats.loc[model_stats['success'].idxmax()]
    best_model_name = model_stats['success'].idxmax()
    print(f"   Best Success Rate: {best_model_name[1]} ({best_model['success']*100:.2f}%)")
    
    # Fastest model
    fastest_model = model_stats.loc[model_stats['latency_sec'].idxmin()]
    fastest_model_name = model_stats['latency_sec'].idxmin()
    print(f"   Fastest Model: {fastest_model_name[1]} ({fastest_model['latency_sec']:.2f}s)")
    
    # Highest throughput
    highest_throughput = model_stats.loc[model_stats['throughput_tps'].idxmax()]
    highest_throughput_name = model_stats['throughput_tps'].idxmax()
    print(f"   Highest Throughput: {highest_throughput_name[1]} ({highest_throughput['throughput_tps']:.2f} tokens/sec)")
    
    # Most reliable provider
    provider_success = df.groupby('llm_provider')['success'].mean()
    most_reliable = provider_success.idxmax()
    reliability_rate = provider_success.max() * 100
    print(f"   Most Reliable Provider: {most_reliable.upper()} ({reliability_rate:.2f}%)")
    
    print(f"\n💡 RECOMMENDATIONS:")
    
    if 'groq' in df['llm_provider'].unique() and 'openrouter' in df['llm_provider'].unique():
        groq_data = df[df['llm_provider'] == 'groq']
        openrouter_data = df[df['llm_provider'] == 'openrouter']
        
        groq_success = (groq_data['success'].sum() / len(groq_data)) * 100
        openrouter_success = (openrouter_data['success'].sum() / len(openrouter_data)) * 100
        
        groq_latency = groq_data['latency_sec'].mean()
        openrouter_latency = openrouter_data['latency_sec'].mean()
        
        if groq_success > openrouter_success:
            print(f"   🏆 GROQ shows better reliability ({groq_success:.1f}% vs {openrouter_success:.1f}%)")
        else:
            print(f"   🏆 OpenRouter shows better reliability ({openrouter_success:.1f}% vs {groq_success:.1f}%)")
        
        if groq_latency < openrouter_latency:
            print(f"   ⚡ GROQ is faster ({groq_latency:.2f}s vs {openrouter_latency:.2f}s)")
        else:
            print(f"   ⚡ OpenRouter is faster ({openrouter_latency:.2f}s vs {groq_latency:.2f}s)")
    
    print(f"\n📊 DATA QUALITY:")
    print(f"   Missing Values: {df.isnull().sum().sum()}")
    print(f"   Duplicate Records: {df.duplicated().sum()}")
    print(f"   Data Completeness: {((len(df) - df.isnull().sum().sum()) / (len(df) * len(df.columns))) * 100:.1f}%")
    
    print(f"\n" + "=" * 60)
    print("✅ Analysis Complete!")

if __name__ == "__main__":
    analyze_data() 