"""
Technology Enrichment Module for DataEnrichmentAgent.

This module provides technology stack enrichment using multiple data sources:
1. BuiltWith API - Website technology detection
2. Job Postings Analysis - Extract tech from job descriptions
3. GitHub API - Open source technology insights
4. Company Website Analysis - Additional tech data

Note: LinkedIn scraping is not recommended due to legal and ethical concerns.
"""

import requests
import re
import json
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse
import time


class TechnologyEnrichment:
    """
    Technology enrichment using multiple data sources.
    
    Provides comprehensive technology stack data for companies
    using legal and ethical data collection methods.
    """
    
    def __init__(self, builtwith_api_key: Optional[str] = None, github_token: Optional[str] = None):
        """
        Initialize technology enrichment with API keys.
        
        Args:
            builtwith_api_key: BuiltWith API key for website technology detection
            github_token: GitHub token for repository analysis
        """
        self.builtwith_api_key = builtwith_api_key
        self.github_token = github_token
        self.session = requests.Session()
        
        # Technology categories for classification
        self.tech_categories = {
            'frontend': [
                'react', 'vue', 'angular', 'javascript', 'typescript', 'html', 'css',
                'sass', 'less', 'webpack', 'babel', 'jquery', 'bootstrap', 'tailwind'
            ],
            'backend': [
                'node.js', 'python', 'java', 'c#', 'php', 'ruby', 'go', 'rust',
                'django', 'flask', 'express', 'spring', 'laravel', 'rails', 'fastapi'
            ],
            'database': [
                'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
                'oracle', 'sqlite', 'dynamodb', 'couchdb', 'neo4j', 'influxdb'
            ],
            'cloud': [
                'aws', 'azure', 'gcp', 'heroku', 'digitalocean', 'linode', 'vultr',
                'cloudflare', 'fastly', 'netlify', 'vercel', 'firebase'
            ],
            'devops': [
                'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions', 'terraform',
                'ansible', 'chef', 'puppet', 'circleci', 'travis', 'azure devops'
            ],
            'mobile': [
                'react native', 'flutter', 'ionic', 'xamarin', 'swift', 'kotlin',
                'android', 'ios', 'cordova', 'phonegap'
            ],
            'ai_ml': [
                'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'opencv',
                'spark', 'hadoop', 'kafka', 'airflow', 'jupyter', 'r'
            ]
        }
    
    def enrich_company_technologies(self, company_domain: str, company_name: str = "") -> Dict[str, Any]:
        """
        Enrich company with technology stack data from multiple sources.
        
        Args:
            company_domain: Company website domain
            company_name: Company name for additional context
            
        Returns:
            Dictionary with technology enrichment data
        """
        technologies = set()
        tech_sources = []
        
        # 1. BuiltWith API (if available)
        if self.builtwith_api_key:
            builtwith_tech = self._get_builtwith_technologies(company_domain)
            if builtwith_tech:
                technologies.update(builtwith_tech)
                tech_sources.append('builtwith')
        
        # 2. Job Postings Analysis
        job_tech = self._get_job_posting_technologies(company_name)
        if job_tech:
            technologies.update(job_tech)
            tech_sources.append('job_postings')
        
        # 3. GitHub Analysis (if company has public repos)
        github_tech = self._get_github_technologies(company_name)
        if github_tech:
            technologies.update(github_tech)
            tech_sources.append('github')
        
        # 4. Website Analysis
        website_tech = self._analyze_website_technologies(company_domain)
        if website_tech:
            technologies.update(website_tech)
            tech_sources.append('website_analysis')
        
        # Categorize technologies
        categorized_tech = self._categorize_technologies(list(technologies))
        
        return {
            'company_technologies': sorted(list(technologies)),
            'company_tech_categories': categorized_tech,
            'company_tech_sources': tech_sources,
            'company_tech_count': len(technologies),
            'company_tech_coverage': len(tech_sources)
        }
    
    def _get_builtwith_technologies(self, domain: str) -> Set[str]:
        """
        Get technologies using BuiltWith API.
        
        Args:
            domain: Company domain
            
        Returns:
            Set of technologies found
        """
        if not self.builtwith_api_key:
            return set()
        
        try:
            # BuiltWith API endpoint
            url = f"https://api.builtwith.com/v20/api.json"
            params = {
                'KEY': self.builtwith_api_key,
                'LOOKUP': domain
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                technologies = set()
                
                # Parse BuiltWith response
                for result in data.get('Results', []):
                    for path in result.get('Result', {}).get('Paths', []):
                        for technology in path.get('Technologies', []):
                            tech_name = technology.get('Name', '').lower()
                            if tech_name:
                                technologies.add(tech_name)
                
                return technologies
            else:
                print(f"BuiltWith API error: {response.status_code}")
                return set()
                
        except Exception as e:
            print(f"BuiltWith API exception: {e}")
            return set()
    
    def _get_job_posting_technologies(self, company_name: str) -> Set[str]:
        """
        Extract technologies from job postings (simulated).
        
        Args:
            company_name: Company name to search for
            
        Returns:
            Set of technologies found in job postings
        """
        if not company_name:
            return set()
        
        # This is a simplified simulation
        # In a real implementation, you would:
        # 1. Search job boards (Indeed, LinkedIn Jobs, etc.)
        # 2. Parse job descriptions
        # 3. Extract technology keywords
        # 4. Use NLP to identify relevant technologies
        
        # Simulated job posting analysis
        simulated_job_tech = {
            'Salesforce': ['salesforce', 'apex', 'lightning', 'salesforce crm', 'mulesoft'],
            'HubSpot': ['hubspot', 'marketing automation', 'crm', 'wordpress', 'javascript'],
            'Slack': ['slack', 'node.js', 'react', 'typescript', 'aws', 'kubernetes'],
            'Zoom': ['zoom', 'video conferencing', 'webrtc', 'javascript', 'python'],
            'Stripe': ['stripe', 'payment processing', 'api', 'python', 'ruby', 'go']
        }
        
        return set(simulated_job_tech.get(company_name, []))
    
    def _get_github_technologies(self, company_name: str) -> Set[str]:
        """
        Analyze GitHub repositories for technology insights.
        
        Args:
            company_name: Company name to search for
            
        Returns:
            Set of technologies found in GitHub repos
        """
        if not self.github_token or not company_name:
            return set()
        
        try:
            # Search for company repositories
            url = "https://api.github.com/search/repositories"
            params = {
                'q': f'org:{company_name.lower()}',
                'sort': 'updated',
                'per_page': 100
            }
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                technologies = set()
                
                # Analyze repository languages
                for repo in data.get('items', []):
                    lang_url = repo.get('languages_url')
                    if lang_url:
                        lang_response = self.session.get(lang_url, headers=headers, timeout=5)
                        if lang_response.status_code == 200:
                            langs = lang_response.json()
                            technologies.update(lang.lower() for lang in langs.keys())
                
                return technologies
            else:
                print(f"GitHub API error: {response.status_code}")
                return set()
                
        except Exception as e:
            print(f"GitHub API exception: {e}")
            return set()
    
    def _analyze_website_technologies(self, domain: str) -> Set[str]:
        """
        Analyze company website for technology indicators.
        
        Args:
            domain: Company domain
            
        Returns:
            Set of technologies found on website
        """
        if not domain:
            return set()
        
        try:
            # Add protocol if missing
            if not domain.startswith(('http://', 'https://')):
                domain = f'https://{domain}'
            
            response = self.session.get(domain, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                technologies = set()
                content = response.text.lower()
                
                # Look for technology indicators in HTML
                tech_indicators = [
                    'react', 'vue', 'angular', 'jquery', 'bootstrap', 'tailwind',
                    'wordpress', 'drupal', 'joomla', 'shopify', 'magento',
                    'google analytics', 'gtag', 'hotjar', 'mixpanel',
                    'stripe', 'paypal', 'braintree', 'square'
                ]
                
                for tech in tech_indicators:
                    if tech in content:
                        technologies.add(tech)
                
                # Look for meta tags and scripts
                meta_patterns = [
                    r'<meta[^>]*generator[^>]*content="([^"]*)"',
                    r'<script[^>]*src="[^"]*/([^/]+)\.js"',
                    r'<link[^>]*href="[^"]*/([^/]+)\.css"'
                ]
                
                for pattern in meta_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if len(match) > 2:  # Filter out very short matches
                            technologies.add(match.lower())
                
                return technologies
            else:
                print(f"Website analysis error: {response.status_code}")
                return set()
                
        except Exception as e:
            print(f"Website analysis exception: {e}")
            return set()
    
    def _categorize_technologies(self, technologies: List[str]) -> Dict[str, List[str]]:
        """
        Categorize technologies into different categories.
        
        Args:
            technologies: List of technology names
            
        Returns:
            Dictionary with categorized technologies
        """
        categorized = {category: [] for category in self.tech_categories.keys()}
        categorized['other'] = []
        
        for tech in technologies:
            tech_lower = tech.lower()
            categorized_flag = False
            
            for category, keywords in self.tech_categories.items():
                if any(keyword in tech_lower for keyword in keywords):
                    categorized[category].append(tech)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                categorized['other'].append(tech)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    def get_technology_insights(self, technologies: List[str]) -> Dict[str, Any]:
        """
        Generate insights about the technology stack.
        
        Args:
            technologies: List of technologies
            
        Returns:
            Dictionary with technology insights
        """
        categorized = self._categorize_technologies(technologies)
        
        insights = {
            'total_technologies': len(technologies),
            'category_distribution': {k: len(v) for k, v in categorized.items()},
            'primary_categories': sorted(
                categorized.keys(), 
                key=lambda x: len(categorized[x]), 
                reverse=True
            )[:3],
            'tech_diversity_score': len(categorized) / len(self.tech_categories),
            'modern_tech_indicators': self._detect_modern_tech(technologies),
            'enterprise_indicators': self._detect_enterprise_tech(technologies)
        }
        
        return insights
    
    def _detect_modern_tech(self, technologies: List[str]) -> List[str]:
        """Detect modern technology indicators."""
        modern_tech = [
            'react', 'vue', 'angular', 'typescript', 'node.js', 'python',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'microservices'
        ]
        
        return [tech for tech in technologies if tech.lower() in modern_tech]
    
    def _detect_enterprise_tech(self, technologies: List[str]) -> List[str]:
        """Detect enterprise technology indicators."""
        enterprise_tech = [
            'salesforce', 'oracle', 'sap', 'microsoft', 'ibm', 'adobe',
            'enterprise', 'erp', 'crm', 'bi', 'analytics'
        ]
        
        return [tech for tech in technologies if tech.lower() in enterprise_tech]


# Example usage and testing
if __name__ == "__main__":
    # Initialize with API keys (if available)
    tech_enrichment = TechnologyEnrichment(
        builtwith_api_key=None,  # Add your BuiltWith API key
        github_token=None        # Add your GitHub token
    )
    
    # Test with a sample company
    result = tech_enrichment.enrich_company_technologies(
        company_domain="salesforce.com",
        company_name="Salesforce"
    )
    
    print("Technology Enrichment Result:")
    print(json.dumps(result, indent=2))
