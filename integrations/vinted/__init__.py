"""
Vinted Integration Module

This module wraps the existing pyVintedVN library and provides:
1. Normalization of Vinted data into internal models
2. Safe integration with the dashboard (errors don't crash the app)
3. Configuration and status tracking
"""

from .adapter import VintedAdapter
from .normalizer import VintedNormalizer

__all__ = ['VintedAdapter', 'VintedNormalizer']
