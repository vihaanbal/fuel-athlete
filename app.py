import os
import json
import secrets
import base64
import hashlib
import hmac
import time
from urllib.parse import quote
from datetime import datetime

import requests
import streamlit as st
import streamlit.components.v1 as components
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from supabase import create_client
from supabase.client import ClientOptions

st.set_page_config(
    page_title="Fuel Coach for Teens",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block');

:root {
    color-scheme: light;
}

html, body, [class*="st-"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background-image:
        linear-gradient(135deg, rgba(245, 236, 220, 0.82) 0%, rgba(237, 231, 219, 0.78) 42%, rgba(216, 231, 228, 0.76) 100%),
        url("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=2400&q=85");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

.block-container {
    max-width: 1400px;
    padding-top: 0.8rem;
    padding-left: 1.65rem;
    padding-right: 1.65rem;
    padding-bottom: 2.5rem;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #173F46 !important;
}

p, label {
    color: #34565B !important;
}

[data-testid="stCaptionContainer"] p {
    color: #6B7777 !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(7, 35, 45, 0.98) 0%, rgba(8, 52, 62, 0.98) 56%, rgba(10, 71, 78, 0.98) 100%);
    border-right: 1px solid rgba(255, 248, 236, 0.16);
    box-shadow: 8px 0 26px rgba(6, 30, 37, 0.18);
}

section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding: 1.2rem 0.6rem 1rem 0.6rem;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.55rem;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(255, 246, 232, 0.14) !important;
}

.sidebar-brand-wrap {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    text-align: left;
    padding: 0.3rem 0.55rem 0.85rem 0.55rem;
    min-width: 0;
}

.sidebar-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 54px;
    height: 54px;
    border-radius: 16px;
    background: linear-gradient(135deg, #F3D99F 0%, #E8C57C 100%);
    color: #153E45;
    font-size: 1.5rem;
    margin-bottom: 0.65rem;
    box-shadow: 0 10px 24px rgba(8, 39, 44, 0.2);
}

.sidebar-brand {
    font-family: 'Space Grotesk', sans-serif;
    color: #FFFDF7 !important;
    font-size: 1.4rem;
    font-weight: 700;
    line-height: 1.15;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.24);
}

.sidebar-sub {
    color: #E7F1EF !important;
    font-size: 0.8rem;
    line-height: 1.45;
    margin-top: 0.3rem;
    text-shadow: 0 1px 6px rgba(0, 0, 0, 0.24);
}

.sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 0.18rem;
    margin: 0.3rem 0 0.8rem 0;
}

.sidebar-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    width: 100%;
    min-width: 0;
    box-sizing: border-box;
    overflow: hidden;
    color: #F8FBFA !important;
    background: transparent;
    border: none;
    border-radius: 15px;
    padding: 0.92rem 0.9rem;
    font-size: 0.94rem;
    font-weight: 600;
    line-height: 1.2;
    text-shadow: 0 1px 5px rgba(0, 0, 0, 0.22);
}

.sidebar-item.active {
    background: linear-gradient(90deg, #8CCB77 0%, #A0D98A 100%);
    color: #12363D !important;
    box-shadow: 0 9px 22px rgba(24, 76, 52, 0.24);
    text-shadow: none;
}

.sidebar-symbol {
    width: 24px;
    min-width: 24px;
    text-align: center;
    font-size: 1.12rem;
    opacity: 0.96;
}

.side-tip {
    background: linear-gradient(180deg, rgba(130, 191, 158, 0.18) 0%, rgba(48, 113, 109, 0.22) 100%);
    border: 1px solid rgba(255, 250, 238, 0.12);
    border-radius: 18px;
    padding: 1rem 0.95rem;
    text-align: left;
    margin: 0.45rem 0.35rem 0.2rem 0.35rem;
}

.side-tip-title {
    color: #FFE3A8 !important;
    font-weight: 700;
    font-size: 0.88rem;
    margin-bottom: 0.34rem;
    text-shadow: 0 1px 5px rgba(0, 0, 0, 0.22);
}

.side-tip-text {
    color: #F7FBFA !important;
    font-size: 0.79rem;
    line-height: 1.5;
    overflow-wrap: anywhere;
}

section[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    color: #FFF8EE !important;
    background: rgba(255, 248, 235, 0.08) !important;
    border: 1px solid rgba(255, 248, 235, 0.14) !important;
    box-shadow: none !important;
    border-radius: 14px !important;
    min-height: 44px !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255, 248, 235, 0.14) !important;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255, 249, 239, 0.92);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(221, 207, 188, 0.92);
    border-radius: 16px;
    padding: 0.8rem 1.15rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 6px 20px rgba(53, 55, 47, 0.10);
}

.topbar-brand {
    font-family: 'Space Grotesk', sans-serif;
    color: #163E46;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.4px;
}

.topbar-sub {
    color: #648084;
    font-size: 0.73rem;
    margin-top: 0.05rem;
}

.topbar-date {
    color: #35575D;
    font-weight: 600;
    font-size: 0.82rem;
}

.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(112deg, rgba(16, 60, 69, 0.96) 0%, rgba(29, 92, 99, 0.92) 54%, rgba(68, 132, 130, 0.88) 100%);
    border: 1px solid rgba(68, 118, 123, 0.95);
    border-radius: 20px;
    padding: 1.65rem 2rem;
    margin-bottom: 0.9rem;
    min-height: 170px;
    display: flex;
    align-items: center;
    box-shadow: 0 10px 28px rgba(33, 72, 77, 0.16);
}

.hero:after {
    content: "RUN • LIFT • PLAY";
    position: absolute;
    right: 2rem;
    bottom: 1.15rem;
    color: rgba(255, 248, 238, 0.26);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    letter-spacing: 1.9px;
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 760px;
}

.hero-eyebrow {
    color: #EAD2AE;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    margin-bottom: 0.25rem;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    color: #FFF9F0;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.12;
}

.hero-text {
    color: #E9F0EE;
    font-size: 0.9rem;
    max-width: 760px;
    margin-top: 0.35rem;
}

.login-hero {
    max-width: 760px;
    margin: 3rem auto 2.25rem auto;
    background: linear-gradient(120deg, rgba(13, 55, 65, 0.96), rgba(34, 103, 108, 0.93) 60%, rgba(93, 151, 145, 0.90));
    border: 1px solid rgba(72, 123, 128, 0.95);
    border-radius: 22px;
    padding: 2.2rem 2rem;
    text-align: center;
    box-shadow: 0 12px 30px rgba(30, 71, 76, 0.20);
}

.login-badge {
    color: #E9D1AE;
    font-weight: 700;
    letter-spacing: 1px;
    font-size: 0.85rem;
}

.login-title {
    color: #FFF9F0;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2rem;
    margin-top: 0.25rem;
}

.login-text {
    color: #E9F0EE;
    margin-top: 0.35rem;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 250, 242, 0.94);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(221, 207, 188, 0.96) !important;
    border-radius: 17px !important;
    box-shadow: 0 8px 24px rgba(58, 59, 50, 0.11);
}

.section-title,
.right-title,
.week-title,
.card-kicker {
    font-family: 'Space Grotesk', sans-serif;
    color: #173F46;
    font-weight: 700;
    letter-spacing: 0.35px;
}

.section-title {
    font-size: 0.98rem;
    margin-bottom: 0.55rem;
}

.right-title,
.week-title {
    font-size: 0.94rem;
    margin-bottom: 0.65rem;
}

.card-kicker {
    font-size: 0.78rem;
    text-align: center;
    color: #557075;
    letter-spacing: 0.8px;
    margin-bottom: 0.5rem;
}

.section-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 25px;
    height: 25px;
    color: #FFF9F0;
    border-radius: 50%;
    margin-right: 7px;
    font-size: 0.8rem;
}

.section-number.teal { background: #3E8D92; }
.section-number.blue { background: #4E7795; }
.section-number.sand { background: #B7814F; }

.field-label,
.mini-label {
    color: #526E73;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin: 0.1rem 0 0.35rem 0;
}

.stTextInput input {
    background: #F8F0E4 !important;
    color: #21464C !important;
    border: 1px solid #D8C8B5 !important;
    border-radius: 9px !important;
}

.stTextInput input::placeholder {
    color: #8A8580 !important;
}

.stTextInput input:focus {
    border-color: #4B9397 !important;
    box-shadow: 0 0 0 1px #4B9397 !important;
}

div[data-baseweb="select"] > div {
    background: #F8F0E4 !important;
    border: 1px solid #D8C8B5 !important;
    border-radius: 9px !important;
}

div[data-baseweb="select"] * {
    color: #21464C !important;
}

div[data-baseweb="popover"],
div[data-baseweb="popover"] ul,
div[role="listbox"] {
    background: #FFF8EF !important;
}

li[role="option"] {
    background: #FFF8EF !important;
    color: #21464C !important;
}

li[role="option"]:hover {
    background: #EEE1D0 !important;
}

li[aria-selected="true"] {
    background: #D7E9E6 !important;
    color: #17454B !important;
}

span[data-baseweb="tag"] {
    background: #DCEBE8 !important;
    color: #21464C !important;
}

.stButton > button {
    border-radius: 9px !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    transition: 0.18s;
}

.stButton > button:hover {
    transform: translateY(-1px);
}

button[kind="primary"] {
    min-height: 48px !important;
    background: linear-gradient(90deg, #397E84 0%, #4C9698 100%) !important;
    border: 1px solid #397E84 !important;
    color: #FFF9F0 !important;
    box-shadow: 0 5px 14px rgba(45, 112, 118, 0.16);
}

button[kind="secondary"] {
    background: #F8F0E4 !important;
    border-color: #D8C8B5 !important;
    color: #244A50 !important;
}

a[data-testid="stLinkButton"] {
    background: #F2E7D7 !important;
    border-color: #D6C5B1 !important;
    color: #21464C !important;
}

div[data-testid="stAlert"] {
    border-radius: 10px !important;
}

[data-testid="stProgress"] > div > div > div > div {
    background: #3E8D92;
    border-radius: 20px;
}

[data-testid="stMetric"] {
    background: #F5EADB;
    border: 1px solid #DCCAB5;
    border-radius: 10px;
    padding: 0.45rem 0.55rem;
    text-align: center;
}

div[role="radiogroup"] {
    display: flex !important;
    width: 100%;
    gap: 0.45rem !important;
}

div[role="radiogroup"] label {
    flex: 1;
    justify-content: center;
    background: #F7EEE2 !important;
    border: 1px solid #DCCDBB !important;
    border-radius: 9px !important;
    padding: 7px 11px !important;
    margin: 0 !important;
}

div[role="radiogroup"] label p,
div[role="radiogroup"] label span {
    color: #36585D !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}

div[role="radiogroup"] label:has(input:checked) {
    background: #DCEBE8 !important;
    border-color: #5B9A9C !important;
}

div[role="radiogroup"] label:has(input:checked) p,
div[role="radiogroup"] label:has(input:checked) span {
    color: #16434A !important;
}

.pill-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin: 0.35rem 0 0.7rem 0;
}

.food-pill {
    display: inline-block;
    background: #E8E1D4;
    border: 1px solid #D7C7B4;
    color: #294C51;
    border-radius: 999px;
    padding: 0.34rem 0.62rem;
    font-size: 0.75rem;
    font-weight: 600;
}

.small-spacer {
    height: 1.63rem;
}

.empty-state {
    text-align: center;
    color: #7C8382;
    line-height: 1.5;
}

.empty-state.compact {
    padding: 2rem 1rem;
}

.gauge-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0.25rem 0;
}

.gauge {
    width: 154px;
    height: 154px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.gauge-inner {
    width: 118px;
    height: 118px;
    background: #FFF9F0;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 0 0 1px #E5D9C9;
}

.gauge-score {
    font-family: 'Space Grotesk', sans-serif;
    color: #173F46;
    font-size: 2.8rem;
    line-height: 1;
    font-weight: 700;
}

.gauge-status {
    color: #3E8D92;
    font-size: 0.9rem;
    font-weight: 700;
    margin-top: 0.25rem;
}

.readiness-message {
    color: #294A50;
    font-size: 1.02rem;
    line-height: 1.45;
    font-weight: 600;
    margin-top: 1.15rem;
    margin-bottom: 0.65rem;
}

.featured-food {
    display: grid;
    grid-template-columns: 56px 1fr;
    gap: 0.85rem;
    align-items: center;
    background: #E8F0E9;
    border: 1px solid #CBDCCA;
    border-radius: 13px;
    padding: 0.9rem;
    margin-bottom: 0.7rem;
}

.featured-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 13px;
    background: #D1E3DD;
    font-size: 1.2rem;
}

.featured-label {
    color: #5B7770;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.8px;
}

.featured-name {
    color: #1E474B;
    font-weight: 700;
    font-size: 0.98rem;
    margin: 0.1rem 0;
}

.featured-reason {
    color: #667675;
    font-size: 0.78rem;
    line-height: 1.4;
}

.mini-food {
    min-height: 58px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    background: #F4EBDD;
    border: 1px solid #DDCFBC;
    color: #294C51;
    border-radius: 10px;
    padding: 0.5rem;
    font-size: 0.75rem;
    font-weight: 600;
}

.recovery-copy {
    color: #617477;
    font-size: 0.83rem;
    margin-bottom: 0.5rem;
}

.recovery-row {
    color: #254A50;
    background: #F4EBDD;
    border: 1px solid #E1D3C0;
    border-radius: 9px;
    padding: 0.48rem 0.65rem;
    margin-bottom: 0.35rem;
    font-size: 0.8rem;
    font-weight: 600;
}

.week-cell {
    text-align: center;
    padding: 0.35rem 0.15rem;
}

.week-cell.muted {
    opacity: 0.45;
}

.week-day {
    color: #557075;
    font-size: 0.72rem;
    font-weight: 700;
}

.week-score {
    color: #173F46;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0.15rem 0 0.35rem 0;
}

.week-bar {
    height: 7px;
    background: #E3D9CB;
    border-radius: 999px;
    overflow: hidden;
}

.week-bar span {
    display: block;
    height: 100%;
    background: linear-gradient(90deg, #3E8D92, #76AAA3);
    border-radius: 999px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #DDCFBC;
    border-radius: 12px;
    overflow: hidden;
}

hr {
    border-color: #DDCFBC !important;
}

@media (max-width: 900px) {
    .hero:after {
        display: none;
    }
    .topbar-date {
        display: none;
    }
}


section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #F8FBFA !important;
}

section[data-testid="stSidebar"] .sidebar-item.active,
section[data-testid="stSidebar"] .sidebar-item.active span,
section[data-testid="stSidebar"] .sidebar-item.active div {
    color: #12363D !important;
}

.sidebar-item span:last-child {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

[data-testid="column"] {
    min-width: 0 !important;
}

.stTextInput,
.stSelectbox,
.stMultiSelect,
.stButton,
[data-testid="stSlider"] {
    min-width: 0 !important;
    max-width: 100% !important;
}

.stTextInput input {
    min-height: 44px !important;
    padding: 0.65rem 0.8rem !important;
    line-height: 1.2 !important;
    box-sizing: border-box !important;
}

div[data-baseweb="select"] > div {
    min-height: 44px !important;
    max-width: 100% !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

div[data-baseweb="select"] span {
    min-width: 0 !important;
    max-width: 100% !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}

div[role="radiogroup"] {
    flex-wrap: wrap !important;
}

div[role="radiogroup"] label {
    min-width: 0 !important;
    min-height: 44px !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[role="radiogroup"] label p,
div[role="radiogroup"] label span {
    max-width: 100% !important;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    text-align: center !important;
    line-height: 1.2 !important;
}

.stButton > button,
a[data-testid="stLinkButton"] {
    width: 100%;
    height: auto !important;
    min-height: 42px !important;
    white-space: normal !important;
    line-height: 1.2 !important;
    overflow-wrap: anywhere !important;
    padding: 0.62rem 0.75rem !important;
    box-sizing: border-box !important;
}

.food-pill,
.mini-food,
.recovery-row,
.featured-name,
.featured-reason,
.food-name,
.food-reason {
    max-width: 100%;
    overflow-wrap: anywhere;
    word-break: normal;
}

.topbar,
.hero,
.login-hero,
.side-tip,
.featured-food,
.mini-food,
.recovery-row,
.food-pill {
    box-sizing: border-box;
}

@media (max-width: 1100px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    div[role="radiogroup"] label {
        flex-basis: calc(50% - 0.45rem) !important;
    }
}


header[data-testid="stHeader"] {
    background: #0B1014 !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.16) !important;
}

header[data-testid="stHeader"] button,
header[data-testid="stHeader"] svg,
header[data-testid="stHeader"] [data-testid="stToolbar"] * {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    background: #0B1014 !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] button,
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] svg {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1450px !important;
    padding-top: 2.65rem !important;
    padding-left: 1.35rem !important;
    padding-right: 1.35rem !important;
    padding-bottom: 2.5rem !important;
}

section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    background: transparent !important;
}

section[data-testid="stSidebar"] .sidebar-brand,
section[data-testid="stSidebar"] .sidebar-sub,
section[data-testid="stSidebar"] .sidebar-item:not(.active),
section[data-testid="stSidebar"] .sidebar-item:not(.active) span,
section[data-testid="stSidebar"] .side-tip-text {
    color: #FFFFFF !important;
    text-shadow: 0 1px 5px rgba(0, 0, 0, 0.28) !important;
}

section[data-testid="stSidebar"] .side-tip-title {
    color: #FFE3A8 !important;
}

section[data-testid="stSidebar"] .sidebar-item.active,
section[data-testid="stSidebar"] .sidebar-item.active span {
    color: #102F36 !important;
    text-shadow: none !important;
}

section[data-testid="stSidebar"] .sidebar-item {
    min-height: 48px;
    padding: 0.82rem 0.9rem;
}

[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 250, 242, 0.97) !important;
    border: 1px solid rgba(211, 196, 176, 0.98) !important;
    box-shadow: 0 10px 26px rgba(55, 54, 47, 0.11) !important;
    overflow: hidden !important;
}

[data-testid="stWidgetLabel"] p {
    color: #31555C !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
    margin-bottom: 0.3rem !important;
}

.stTextInput,
.stSelectbox,
.stMultiSelect,
[data-testid="stSlider"] {
    width: 100% !important;
    min-width: 0 !important;
    overflow: visible !important;
}

.stTextInput input {
    width: 100% !important;
    height: 46px !important;
    min-height: 46px !important;
    padding: 0 0.85rem !important;
    border: 1px solid #CBBCA9 !important;
    border-radius: 10px !important;
    background: #FFFCF7 !important;
    color: #173F46 !important;
    font-size: 0.86rem !important;
    line-height: 46px !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}

div[data-baseweb="select"] {
    width: 100% !important;
    min-width: 0 !important;
}

div[data-baseweb="select"] > div {
    width: 100% !important;
    min-width: 0 !important;
    min-height: 46px !important;
    height: auto !important;
    padding-left: 0.15rem !important;
    padding-right: 0.15rem !important;
    border: 1px solid #CBBCA9 !important;
    border-radius: 10px !important;
    background: #FFFCF7 !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

div[data-baseweb="select"] > div > div {
    min-width: 0 !important;
    max-width: 100% !important;
    overflow: hidden !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] p {
    color: #173F46 !important;
    max-width: 100% !important;
    min-width: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    font-size: 0.84rem !important;
}

span[data-baseweb="tag"] {
    max-width: 100% !important;
    min-height: 28px !important;
    overflow: hidden !important;
}

span[data-baseweb="tag"] span {
    max-width: 150px !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}

div[role="radiogroup"] {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
    gap: 0.5rem !important;
    width: 100% !important;
}

div[role="radiogroup"] label {
    width: 100% !important;
    min-width: 0 !important;
    min-height: 46px !important;
    padding: 0.55rem 0.55rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.35rem !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

div[role="radiogroup"] label p,
div[role="radiogroup"] label span {
    min-width: 0 !important;
    max-width: 100% !important;
    color: #254B52 !important;
    font-size: 0.76rem !important;
    line-height: 1.15 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

a[data-testid="stLinkButton"] {
    min-height: 46px !important;
    background: #123847 !important;
    border: 1px solid #123847 !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
}

a[data-testid="stLinkButton"] p,
a[data-testid="stLinkButton"] span,
a[data-testid="stLinkButton"] div {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

[data-testid="stMetric"] {
    min-height: 78px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: hidden !important;
}

.empty-state.compact {
    min-height: 142px !important;
    padding: 1.25rem 1rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.right-title,
.section-title,
.week-title,
.card-kicker {
    color: #123F47 !important;
}

.topbar-brand,
.topbar-date {
    color: #123A43 !important;
}

.topbar-sub {
    color: #55727A !important;
}

@media (max-width: 1100px) {
    [data-testid="stMainBlockContainer"] {
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
    }

    div[role="radiogroup"] {
        grid-template-columns: 1fr !important;
    }

    div[role="radiogroup"] label p,
    div[role="radiogroup"] label span {
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
}


.sidebar-button-gap {
    height: 0.65rem;
}

.side-tip {
    margin-bottom: 0.2rem !important;
}

[data-testid="stWidgetLabel"] {
    display: block !important;
    min-height: 1.35rem !important;
    margin-bottom: 0.32rem !important;
    padding-left: 0.08rem !important;
    overflow: visible !important;
}

[data-testid="stWidgetLabel"] p {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    line-height: 1.3 !important;
    font-size: 0.8rem !important;
}

.stTextInput,
.stSelectbox,
.stMultiSelect,
[data-testid="stNumberInput"],
[data-testid="stSlider"] {
    width: 100% !important;
    min-width: 0 !important;
    margin-bottom: 0.55rem !important;
}

.stTextInput input {
    height: 50px !important;
    min-height: 50px !important;
    padding: 0 0.95rem !important;
    line-height: 1.25 !important;
    font-size: 0.9rem !important;
}

div[data-baseweb="select"] > div {
    min-height: 50px !important;
    height: 50px !important;
    padding: 0 0.6rem !important;
    display: flex !important;
    align-items: center !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] p {
    font-size: 0.88rem !important;
    line-height: 1.25 !important;
}

[data-testid="stNumberInput"] > div {
    width: 100% !important;
    min-width: 0 !important;
}

[data-testid="stNumberInput"] input {
    height: 50px !important;
    min-height: 50px !important;
    background: #FFFCF7 !important;
    color: #173F46 !important;
    border-top: 1px solid #CBBCA9 !important;
    border-bottom: 1px solid #CBBCA9 !important;
    font-size: 0.9rem !important;
    text-align: center !important;
    box-sizing: border-box !important;
}

[data-testid="stNumberInput"] button {
    min-width: 46px !important;
    width: 46px !important;
    height: 50px !important;
    min-height: 50px !important;
    padding: 0 !important;
    background: #F2E7D7 !important;
    border-color: #CBBCA9 !important;
    color: #173F46 !important;
    box-sizing: border-box !important;
}

[data-testid="stNumberInput"] button svg {
    fill: #173F46 !important;
}

[data-testid="stSlider"] {
    overflow: visible !important;
    padding: 0.15rem 0.2rem 0.45rem 0.2rem !important;
}

div[role="radiogroup"] {
    gap: 0.65rem !important;
}

div[role="radiogroup"] label {
    min-height: 50px !important;
    padding: 0.62rem 0.65rem !important;
}

div[role="radiogroup"] label p,
div[role="radiogroup"] label span {
    font-size: 0.78rem !important;
    line-height: 1.2 !important;
}

[data-testid="stMainBlockContainer"] [data-testid="column"] {
    min-width: 0 !important;
    overflow: visible !important;
}

[data-testid="stMainBlockContainer"] [data-testid="column"] > div {
    min-width: 0 !important;
    overflow: visible !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"] {
    overflow: visible !important;
}

section[data-testid="stSidebar"] .sidebar-item {
    min-height: 50px !important;
    padding-top: 0.9rem !important;
    padding-bottom: 0.9rem !important;
}

section[data-testid="stSidebar"] .side-tip {
    overflow: visible !important;
}

section[data-testid="stSidebar"] .side-tip-text {
    white-space: normal !important;
    overflow: visible !important;
    line-height: 1.55 !important;
}

@media (max-width: 1180px) {
    .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    div[role="radiogroup"] {
        grid-template-columns: 1fr !important;
    }
}



section[data-testid="stSidebar"] .stButton {
    margin: 0.08rem 0 !important;
}

section[data-testid="stSidebar"] .stButton > button {
    justify-content: flex-start !important;
    text-align: left !important;
    min-height: 48px !important;
    padding: 0.82rem 0.95rem !important;
    border-radius: 15px !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #F7FBFA !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.09) !important;
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #8CCB77 0%, #A0D98A 100%) !important;
    color: #12363D !important;
    border: none !important;
    box-shadow: 0 9px 22px rgba(24, 76, 52, 0.24) !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] p {
    color: #12363D !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"] p {
    color: #F7FBFA !important;
}

section[data-testid="stSidebar"] .stButton > button p {
    white-space: pre !important;
    width: 100% !important;
    text-align: left !important;
    line-height: 1.2 !important;
}

section[data-testid="stSidebar"] .st-key-nav_Water button p,
section[data-testid="stSidebar"] [class*="st-key-nav_Water"] button p {
    transform: translateX(4px) !important;
}

.nav-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.14);
    margin: 0.8rem 0 0.7rem 0;
}

.page-heading {
    font-family: 'Space Grotesk', sans-serif;
    color: #173F46;
    font-size: 1.35rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}

.page-subheading {
    color: #687878;
    font-size: 0.88rem;
    margin-bottom: 1rem;
}

.guide-title {
    color: #173F46;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.45rem;
}

.guide-copy {
    color: #5F7072;
    font-size: 0.86rem;
    line-height: 1.55;
}

.settings-row {
    color: #294A50;
    font-size: 0.9rem;
    line-height: 1.6;
}


.insight-metric-card {
    min-height: 124px;
    border-radius: 17px;
    padding: 1rem 1.1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    border: 1px solid rgba(36, 76, 83, 0.14);
    box-shadow: 0 8px 20px rgba(54, 58, 51, 0.08);
    overflow: hidden;
}

.insight-metric-card.checkins {
    background: linear-gradient(135deg, #E4F0ED 0%, #D8E8E5 100%);
}

.insight-metric-card.average {
    background: linear-gradient(135deg, #E6EDF4 0%, #DAE4EE 100%);
}

.insight-metric-card.best {
    background: linear-gradient(135deg, #EAF1E3 0%, #DCE8D3 100%);
}

.insight-metric-card.latest {
    background: linear-gradient(135deg, #F2E6D4 0%, #EAD9C2 100%);
}

.insight-metric-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}

.insight-metric-icon {
    width: 36px;
    height: 36px;
    border-radius: 11px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.58);
    color: #245159;
    font-size: 1rem;
    flex: 0 0 auto;
}

.insight-metric-label {
    color: #425F64;
    font-size: 0.78rem;
    line-height: 1.25;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.55px;
    overflow-wrap: anywhere;
}

.insight-metric-value {
    color: #173F46;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.45rem;
    line-height: 1;
    font-weight: 700;
    margin-top: 0.75rem;
}

.feedback-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.65rem;
    margin-top: 0.35rem;
}

.feedback-chip {
    border-radius: 13px;
    padding: 0.8rem 0.55rem;
    text-align: center;
    border: 1px solid rgba(31, 76, 82, 0.13);
}

.feedback-chip.great {
    background: #E5F1E4;
}

.feedback-chip.okay {
    background: #F1E8D7;
}

.feedback-chip.low {
    background: #F2DEDB;
}

.feedback-number {
    color: #173F46;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.65rem;
    line-height: 1;
    font-weight: 700;
}

.feedback-label {
    color: #5C6F72;
    font-size: 0.76rem;
    font-weight: 700;
    margin-top: 0.35rem;
}

.guide-card {
    min-height: 190px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    background: rgba(255, 250, 242, 0.97);
    border: 1px solid #D8C8B5;
    border-top-width: 5px;
    border-radius: 17px;
    padding: 1.25rem 1.3rem 1.35rem 1.3rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 22px rgba(58, 59, 50, 0.09);
    overflow: hidden;
}

.guide-card.quick {
    border-top-color: #4B9498;
}

.guide-card.balance {
    border-top-color: #6E88A4;
}

.guide-card.hydration {
    border-top-color: #4A82AE;
}

.guide-card.recovery {
    border-top-color: #7A8E62;
}

.guide-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #E6EFED;
    color: #235058;
    font-size: 1.12rem;
    margin-bottom: 0.75rem;
}

.guide-card .guide-title {
    color: #173F46;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    line-height: 1.3;
    font-weight: 700;
    margin-bottom: 0.55rem;
    overflow-wrap: anywhere;
}

.guide-card .guide-copy {
    color: #526A6E;
    font-size: 0.88rem;
    line-height: 1.65;
    overflow-wrap: anywhere;
    word-break: normal;
}

div[data-testid="stTextInput"]:has(input[aria-label="Email"]) div[data-baseweb="input"],
div[data-testid="stTextInput"]:has(input[aria-label="Password"]) div[data-baseweb="input"] {
    min-height: 50px !important;
    display: flex !important;
    align-items: center !important;
}

input[aria-label="Email"],
input[aria-label="Password"] {
    height: 50px !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 0.9rem !important;
    text-align: left !important;
    font-size: 0.95rem !important;
    line-height: normal !important;
    letter-spacing: 0.1px !important;
    box-sizing: border-box !important;
}

input[aria-label="Password"] {
    padding-right: 2.8rem !important;
}

div[data-testid="stTextInput"]:has(input[aria-label="Email"]),
div[data-testid="stTextInput"]:has(input[aria-label="Password"]) {
    max-width: 520px;
    margin-left: auto !important;
    margin-right: auto !important;
}

div[data-testid="stTextInput"]:has(input[aria-label="Email"]) [data-testid="stWidgetLabel"],
div[data-testid="stTextInput"]:has(input[aria-label="Password"]) [data-testid="stWidgetLabel"] {
    text-align: left !important;
}


[data-testid="stNumberInput"] div[data-baseweb="input"] {
    min-height: 52px !important;
    height: 52px !important;
    display: flex !important;
    align-items: stretch !important;
    overflow: hidden !important;
    border-radius: 10px !important;
}

[data-testid="stNumberInput"] input {
    height: 52px !important;
    min-height: 52px !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    line-height: 52px !important;
    text-align: center !important;
}

[data-testid="stNumberInput"] button {
    width: 50px !important;
    min-width: 50px !important;
    height: 52px !important;
    min-height: 52px !important;
    padding: 0 !important;
    margin: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
}

[data-testid="stNumberInput"] button > div,
[data-testid="stNumberInput"] button span {
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    margin: 0 !important;
}

[data-testid="stNumberInput"] button svg {
    display: block !important;
    width: 18px !important;
    height: 18px !important;
    margin: auto !important;
    position: static !important;
    transform: none !important;
}

a[data-testid="stLinkButton"],
a[data-testid^="stBaseLinkButton"],
[data-testid="stLinkButton"] a {
    min-height: 50px !important;
    height: 50px !important;
    background: #347F86 !important;
    border: 1px solid #347F86 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 6px 16px rgba(36, 94, 101, 0.18) !important;
    opacity: 1 !important;
}

a[data-testid="stLinkButton"]:hover,
a[data-testid^="stBaseLinkButton"]:hover,
[data-testid="stLinkButton"] a:hover {
    background: #286C73 !important;
    border-color: #286C73 !important;
}

a[data-testid="stLinkButton"] *,
a[data-testid^="stBaseLinkButton"] *,
[data-testid="stLinkButton"] a * {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    opacity: 1 !important;
    font-weight: 700 !important;
    text-shadow: none !important;
}

.login-kicker {
    margin-bottom: 0.45rem !important;
}

div[data-testid="stExpander"] {
    width: 100% !important;
    margin: 0.65rem 0 0 0 !important;
    border: 1px solid #D8C8B5 !important;
    border-radius: 12px !important;
    background: #FFFCF7 !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"] details {
    overflow: hidden !important;
}

div[data-testid="stExpanderDetails"] {
    padding: 0.62rem 0.85rem 0.82rem 0.85rem !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

.reset-help-text {
    color: #667C80 !important;
    font-size: 0.84rem !important;
    line-height: 1.35 !important;
    margin: 0.34rem 0 0.6rem 0.35rem !important;
    padding: 0 !important;
}

div[data-testid="stExpanderDetails"] .stButton {
    width: 100% !important;
    margin: 0 !important;
}

div[data-testid="stExpanderDetails"] .stButton > button {
    min-height: 46px !important;
    height: 46px !important;
    padding: 0 0.9rem !important;
}

.manage-food-list {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin: -0.62rem -0.85rem 0.9rem -0.85rem;
    background: #F5EEE3;
    border-bottom: 1px solid #DCCDBB;
}

.manage-food-card {
    width: 100%;
    background: #F5EEE3;
    border: none;
    border-bottom: 1px solid #DCCDBB;
    border-radius: 0;
    padding: 0.78rem 1rem;
    box-sizing: border-box;
    overflow: hidden;
}

.manage-food-card:last-child {
    border-bottom: none;
}

.manage-food-name {
    color: #214A50;
    font-size: 0.86rem;
    font-weight: 700;
    line-height: 1.3;
    margin-bottom: 0.32rem;
    overflow-wrap: anywhere;
}

.manage-food-macros {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem 0.8rem;
    color: #61777A;
    font-size: 0.77rem;
    line-height: 1.35;
}

.manage-food-macro {
    white-space: nowrap;
}

.manage-food-macro b {
    color: #345C61;
    font-weight: 700;
}

.manage-remove-label {
    color: #31555C;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 0.1rem 0 0.4rem 0.08rem;
}

@media (max-width: 1000px) {
    .insight-metric-card {
        min-height: 112px;
    }

    .insight-metric-value {
        font-size: 2rem;
    }

    .guide-card {
        min-height: auto;
    }
}



/* Final alignment and contrast fixes */
[data-testid="stNumberInput"] button {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    line-height: 1 !important;
}

[data-testid="stNumberInput"] button > div,
[data-testid="stNumberInput"] button span {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    height: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

[data-testid="stNumberInput"] button > div,
[data-testid="stNumberInput"] button > span {
    transform: translateY(-3px) !important;
}

[data-testid="stNumberInput"] button svg {
    width: 18px !important;
    height: 18px !important;
    margin: 0 !important;
    position: static !important;
    top: auto !important;
    transform: none !important;
}

div[data-testid="stTextInput"]:has(input[aria-label="Search for a food you have"]) div[data-baseweb="input"] {
    height: 50px !important;
    min-height: 50px !important;
    display: flex !important;
    align-items: center !important;
    overflow: hidden !important;
}

input[aria-label="Search for a food you have"] {
    height: 50px !important;
    min-height: 50px !important;
    padding: 0 1rem !important;
    line-height: normal !important;
    box-sizing: border-box !important;
}

button[kind="primary"],
button[kind="primary"] p,
button[kind="primary"] span,
button[kind="primary"] div,
button[kind="primary"] svg {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    opacity: 1 !important;
    text-shadow: none !important;
}

.hero .hero-eyebrow,
.hero .hero-title,
.hero .hero-text,
.login-hero .login-badge,
.login-hero .login-title,
.login-hero .login-text {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

/* Manage-food spacing fix */
div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stExpanderDetails"] {
    padding-left: 0.18rem !important;
    padding-right: 0.18rem !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) .manage-food-list {
    margin-left: -0.18rem !important;
    margin-right: -0.18rem !important;
    margin-bottom: 0.72rem !important;
}

div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) {
    width: calc(100% - 0.20rem) !important;
    margin-left: 0.10rem !important;
    margin-right: 0.10rem !important;
    margin-bottom: 0.18rem !important;
}

div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) [data-testid="stWidgetLabel"] {
    padding-left: 0.22rem !important;
    margin-bottom: 0.30rem !important;
}

div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"] > div {
    width: 100% !important;
}


/* Corrected control alignment and Manage Foods layout */
[data-testid="stNumberInput"] button > div,
[data-testid="stNumberInput"] button > span,
[data-testid="stNumberInput"] button span {
    transform: none !important;
}

[data-testid="stNumberInput"] button svg {
    position: relative !important;
    top: -5px !important;
    transform: none !important;
}

div[data-testid="stCheckbox"] {
    margin-top: 0.08rem !important;
    margin-bottom: 0.08rem !important;
}

div[data-testid="stCheckbox"] label {
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    min-height: 28px !important;
    padding: 0 !important;
    margin: 0 !important;
}

div[data-testid="stCheckbox"] label > div:first-child {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
    align-self: center !important;
}

div[data-testid="stCheckbox"] label p,
div[data-testid="stCheckbox"] label span {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    line-height: 1.2 !important;
    align-self: center !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stExpanderDetails"] {
    padding-left: 0 !important;
    padding-right: 0 !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) .manage-food-list {
    margin-left: 0 !important;
    margin-right: 0 !important;
    margin-bottom: 0.72rem !important;
}

div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) {
    width: 100% !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    margin-bottom: 0.18rem !important;
    box-sizing: border-box !important;
}

div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) [data-testid="stWidgetLabel"] {
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
    margin-bottom: 0.3rem !important;
}

div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"] {
    width: 100% !important;
    max-width: 100% !important;
}

div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"] > div {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    border-left-width: 1px !important;
    border-right-width: 1px !important;
    border-radius: 0 0 10px 10px !important;
    box-sizing: border-box !important;
}

div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"] span,
div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"] p {
    padding-left: 0.18rem !important;
}



/* Final control-position and Manage Foods edge fix */
[data-testid="stNumberInput"] button svg {
    position: relative !important;
    top: auto !important;
    transform: translateY(-10px) !important;
}

div[data-testid="stCheckbox"] label > div:first-child {
    position: relative !important;
    top: -4px !important;
    transform: none !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stExpanderDetails"] {
    padding-left: 0 !important;
    padding-right: 0 !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) {
    width: calc(100% + 1.70rem) !important;
    max-width: none !important;
    margin-left: -0.85rem !important;
    margin-right: -0.85rem !important;
    margin-top: 0 !important;
    margin-bottom: -0.82rem !important;
    padding: 0.62rem 0.85rem 0.82rem 0.85rem !important;
    background: #FFFCF7 !important;
    border-top: 1px solid #DCCDBB !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) [data-testid="stWidgetLabel"] {
    padding-left: 0.08rem !important;
    padding-right: 0 !important;
    margin-bottom: 0.35rem !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"],
div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"] > div {
    width: 100% !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"] > div {
    border-radius: 10px !important;
}


/* Precise final positioning */
[data-testid="stNumberInput"] button svg {
    position: relative !important;
    top: auto !important;
    transform: translateY(-9px) !important;
}

div[data-testid="stCheckbox"] label > div:first-child {
    position: relative !important;
    top: auto !important;
    transform: translateY(-10px) !important;
}

/* Make the entire Remove a food area run edge-to-edge inside Manage foods */
div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stExpanderDetails"] {
    padding-left: 0 !important;
    padding-right: 0 !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 0 -0.82rem 0 !important;
    padding: 0.62rem 0 0.82rem 0 !important;
    background: #FFFCF7 !important;
    border-top: 1px solid #DCCDBB !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) [data-testid="stWidgetLabel"] {
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
    margin-bottom: 0.35rem !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"],
div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"] > div {
    width: 100% !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has([aria-label="Remove a food"]) div[data-testid="stSelectbox"]:has([aria-label="Remove a food"]) div[data-baseweb="select"] > div {
    border-left-width: 1px !important;
    border-right-width: 1px !important;
    border-radius: 0 0 10px 10px !important;
}


/* True final fixes for number controls, warning checkbox, Manage Foods, and login eye */
[data-testid="stNumberInput"] button svg {
    position: relative !important;
    top: auto !important;
    transform: translateY(-7px) !important;
}

/* Move the actual checkbox control, not its text wrapper. */
div[data-testid="stCheckbox"] label > *:has(input[type="checkbox"]),
div[data-testid="stCheckbox"] label > span:first-child {
    position: relative !important;
    top: auto !important;
    transform: translateY(-20px) !important;
    margin: 0 !important;
}

div[data-testid="stCheckbox"] label p,
div[data-testid="stCheckbox"] label div:not(:has(input[type="checkbox"])) {
    transform: none !important;
    top: auto !important;
}

.remove-food-marker {
    display: block !important;
    width: 100% !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* The marker makes this target the Manage Foods expander reliably. */
div[data-testid="stExpander"]:has(.remove-food-marker) div[data-testid="stExpanderDetails"] {
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-bottom: 0 !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"]:has(.remove-food-marker) div[data-testid="stExpanderDetails"] > div,
div[data-testid="stExpander"]:has(.remove-food-marker) div[data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 100% !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
}

div[data-testid="stExpander"]:has(.remove-food-marker) .manage-food-list {
    width: 100% !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    margin-bottom: 0 !important;
}

div[data-testid="stExpander"]:has(.remove-food-marker) div[data-testid="stElementContainer"]:has(div[data-testid="stSelectbox"]),
div[data-testid="stExpander"]:has(.remove-food-marker) div[data-testid="element-container"]:has(div[data-testid="stSelectbox"]) {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stExpander"]:has(.remove-food-marker) div[data-testid="stSelectbox"] {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: 0 !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has(.remove-food-marker) div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] {
    width: 100% !important;
    margin: 0 !important;
    padding: 0.62rem 0.75rem 0.35rem 0.75rem !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has(.remove-food-marker) div[data-testid="stSelectbox"] div[data-baseweb="select"],
div[data-testid="stExpander"]:has(.remove-food-marker) div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has(.remove-food-marker) div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    border-left: 0 !important;
    border-right: 0 !important;
    border-bottom: 0 !important;
    border-radius: 0 !important;
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
}

/* Center the login password visibility icon inside the right-side button. */
div[data-testid="stTextInput"]:has(input[aria-label="Password"]) button {
    width: 44px !important;
    min-width: 44px !important;
    height: 50px !important;
    min-height: 50px !important;
    padding: 0 !important;
    margin: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="stTextInput"]:has(input[aria-label="Password"]) button > div,
div[data-testid="stTextInput"]:has(input[aria-label="Password"]) button span {
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    margin: 0 !important;
}

div[data-testid="stTextInput"]:has(input[aria-label="Password"]) button svg {
    position: static !important;
    transform: none !important;
    margin: 0 auto !important;
}

div[data-testid="stCheckbox"] label > *:has(input[type="checkbox"]),
div[data-testid="stCheckbox"] label > div:first-child,
div[data-testid="stCheckbox"] label > span:first-child {
    position: relative !important;
    top: auto !important;
    transform: translateY(-6px) !important;
    margin: 0 !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stExpanderDetails"] {
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-bottom: 0 !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 100% !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    gap: 0 !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) .manage-food-list {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stSelectbox"] {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] {
    width: 100% !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0.72rem 0.75rem 0.42rem 0.75rem !important;
    border: 0 !important;
    background: transparent !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    width: calc(100% + 2px) !important;
    max-width: none !important;
    margin-left: -1px !important;
    margin-right: -1px !important;
    padding: 0 !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 50px !important;
    height: 50px !important;
    margin: 0 !important;
    padding-left: 0.75rem !important;
    padding-right: 0.75rem !important;
    border-left: 0 !important;
    border-right: 0 !important;
    border-bottom: 0 !important;
    border-top: 1px solid #DCCDBB !important;
    border-radius: 0 !important;
    background: #FFFCF7 !important;
    box-shadow: none !important;
    box-sizing: border-box !important;
}


/* Final Manage Foods spacing + login password-eye alignment */
div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stExpanderDetails"] {
    padding: 0 !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: 100% !important;
    gap: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) .manage-food-list {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    border-bottom: 1px solid #DCCDBB !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stSelectbox"] {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: #FFFCF7 !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] {
    width: 100% !important;
    min-height: 54px !important;
    height: 54px !important;
    display: flex !important;
    align-items: center !important;
    margin: 0 !important;
    padding: 0 0.85rem !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    background: #FFFCF7 !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.2 !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 52px !important;
    height: 52px !important;
    margin: 0 !important;
    padding-left: 0.85rem !important;
    padding-right: 0.85rem !important;
    border-top: 1px solid #DCCDBB !important;
    border-left: none !important;
    border-right: none !important;
    border-bottom: none !important;
    border-radius: 0 !important;
    outline: none !important;
    box-shadow: none !important;
    background: #FFFCF7 !important;
    box-sizing: border-box !important;
}

div[data-testid="stTextInput"]:has(input[aria-label="Password"]) button {
    width: 44px !important;
    min-width: 44px !important;
    height: 50px !important;
    min-height: 50px !important;
    padding: 0 !important;
    margin: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="stTextInput"]:has(input[aria-label="Password"]) button svg {
    position: relative !important;
    left: 4px !important;
    top: 0 !important;
    transform: none !important;
    margin: 0 !important;
}


/* Final Manage Foods card shape: flush to header, outer-radius match */
div[data-testid="stExpander"]:has(.manage-food-list) .manage-food-list {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 0 0.82rem 0 !important;
    padding: 0 !important;
    border: none !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: #F5EEE3 !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) .manage-food-card {
    width: 100% !important;
    margin: 0 !important;
    padding: 0.84rem 0.85rem 1.12rem 0.85rem !important;
    background: #F5EEE3 !important;
    border-left: none !important;
    border-right: none !important;
    border-radius: 0 !important;
    box-sizing: border-box !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) .manage-food-card:first-child {
    border-top-left-radius: 12px !important;
    border-top-right-radius: 12px !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) .manage-food-card:last-child {
    border-bottom-left-radius: 12px !important;
    border-bottom-right-radius: 12px !important;
    border-bottom: none !important;
}

.water-tracker {
    margin: 0.2rem 0 0.65rem 0;
    padding: 0.85rem 0.9rem 0.8rem 0.9rem;
    background: #F2F7F6;
    border: 1px solid #C9DEDB;
    border-radius: 12px;
    box-sizing: border-box;
}

.water-page-intro {
    color: #506D72;
    font-size: 0.9rem;
    margin: 0.05rem 0.9rem 0.95rem 0.9rem;
    line-height: 1.5;
}

.water-summary-card {
    background: linear-gradient(135deg, rgba(236, 248, 247, 0.98) 0%, rgba(218, 239, 238, 0.98) 100%);
    border: 1px solid #B9D6D3;
    border-radius: 20px;
    padding: 1.05rem 1.15rem;
    box-shadow: 0 9px 24px rgba(29, 76, 81, 0.09);
    margin-bottom: 1rem;
}

.water-summary-top {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}

.water-summary-label {
    color: #3A6269;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
}

.water-summary-number {
    color: #143F47;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.15rem;
    font-weight: 700;
    line-height: 1;
    margin-top: 0.22rem;
}

.water-summary-number span {
    color: #658083;
    font-family: 'Poppins', sans-serif;
    font-size: 0.84rem;
    font-weight: 600;
    margin-left: 0.28rem;
}

.water-progress-track {
    height: 12px;
    width: 100%;
    overflow: hidden;
    border-radius: 999px;
    background: rgba(67, 111, 116, 0.12);
    margin: 0.9rem 0 0.8rem 0;
}

.water-progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #327E86 0%, #64B5B4 100%);
    transition: width 0.25s ease;
}

.water-stats-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.65rem;
}

.water-stat-pill {
    background: rgba(255, 252, 247, 0.92);
    border: 1px solid rgba(203, 198, 184, 0.85);
    border-radius: 13px;
    padding: 0.62rem 0.72rem;
}

.water-stat-title {
    color: #728486;
    font-size: 0.64rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.water-stat-value {
    color: #173F46;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    margin-top: 0.12rem;
}

.water-cup-board {
    background: rgba(255, 250, 242, 0.97);
    border: 1px solid #D7C8B6;
    border-radius: 19px;
    padding: 1.15rem;
    min-height: 470px;
    box-shadow: 0 8px 22px rgba(58, 59, 50, 0.08);
    box-sizing: border-box;
}

.water-board-heading {
    color: #173F46;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.92rem;
    font-weight: 700;
    margin-bottom: 0.18rem;
}

.water-board-sub {
    color: #6C7D7F;
    font-size: 0.76rem;
    margin-bottom: 0.8rem;
}

.water-cup-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.7rem;
}

.water-cup-card {
    min-width: 0;
    background: #FFFCF7;
    border: 1px solid #DDD2C4;
    border-radius: 16px;
    padding: 0.72rem 0.45rem 0.62rem 0.45rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(43, 55, 53, 0.04);
}

.water-cup-card.filled {
    background: linear-gradient(180deg, #E8F6F5 0%, #F5FBFA 100%);
    border-color: #82B9BA;
}

.water-cup-visual {
    width: 44px;
    height: 58px;
    margin: 0 auto 0.5rem auto;
    position: relative;
    overflow: hidden;
    border: 3px solid #3B6870;
    border-top-width: 4px;
    border-radius: 11px 11px 14px 14px;
    background: rgba(255, 255, 255, 0.72);
}

.water-cup-visual:after {
    content: "";
    position: absolute;
    left: 5px;
    right: 5px;
    top: 5px;
    height: 2px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.72);
    z-index: 2;
}

.water-cup-fill {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(180deg, #7BD1D5 0%, #3E9EA3 100%);
    transition: height 0.25s ease;
}

.water-cup-number {
    color: #173F46;
    font-size: 0.77rem;
    font-weight: 700;
}

.water-cup-status {
    color: #839092;
    font-size: 0.67rem;
    margin-top: 0.05rem;
}

.water-cup-card.filled .water-cup-status {
    color: #2D7E7E;
    font-weight: 700;
}

.water-control-card {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
    box-shadow: none;
    margin-bottom: 0.55rem;
}

.water-control-shell-marker {
    display: none;
}

[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.water-control-shell-marker) {
    background: rgba(255, 250, 242, 0.97) !important;
    border: 1px solid #D7C8B6 !important;
    border-radius: 19px !important;
    min-height: 470px !important;
    height: 100% !important;
    box-shadow: 0 8px 22px rgba(58, 59, 50, 0.08) !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.water-control-shell-marker) div[data-testid="stVerticalBlock"] {
    padding: 1.15rem !important;
    gap: 0.65rem !important;
    box-sizing: border-box !important;
}

.water-control-title {
    color: #173F46;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.94rem;
    font-weight: 700;
}

.water-control-copy {
    color: #657B7E;
    font-size: 0.78rem;
    line-height: 1.55;
    margin-top: 0.3rem;
    margin-bottom: 0.55rem;
    padding-right: 0.15rem;
}

.water-goal-card {
    margin-top: 0.8rem;
    background: linear-gradient(135deg, #E5F5EA 0%, #F7FCF8 100%);
    border: 1px solid #A9D2B5;
    border-radius: 20px;
    padding: 1rem 0.95rem;
    text-align: center;
    box-shadow: 0 10px 24px rgba(61, 123, 86, 0.10);
}

.water-goal-badge {
    width: 74px;
    height: 74px;
    margin: 0 auto 0.65rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    background: radial-gradient(circle at 30% 30%, #FFFFFF 0%, #E8F8EE 52%, #BCE4C9 100%);
    font-size: 2rem;
    box-shadow: 0 0 0 8px rgba(255,255,255,0.55), 0 0 0 15px rgba(188, 228, 201, 0.24);
    animation: waterGoalPulse 1.6s ease-in-out infinite;
}

.water-goal-title {
    color: #1D6849;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.22rem;
    font-weight: 700;
}

.water-goal-text {
    color: #49725D;
    font-size: 0.82rem;
    line-height: 1.45;
    margin-top: 0.24rem;
}

.water-next-card {
    margin-top: 0.8rem;
    padding: 0.9rem 0.95rem;
    border: 1px dashed #D1BC91;
    border-radius: 15px;
    background: rgba(255, 252, 246, 0.9);
    color: #576F72;
    font-size: 0.79rem;
    line-height: 1.5;
}

@keyframes waterGoalPulse {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-3px) scale(1.035); }
}

section[data-testid="stSidebar"] .stButton > button p {
    white-space: pre !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) .manage-food-list {
    box-shadow: inset 0 0 0 1px #DCCDBB !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) .manage-food-card {
    position: relative !important;
    z-index: 1 !important;
}

div[data-testid="stExpander"]:has(.manage-food-list) div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    border: none !important;
    border-radius: 10px !important;
    box-shadow: inset 0 0 0 1px #DCCDBB !important;
    background: #FFFCF7 !important;
}

@media (max-width: 1000px) {
    .water-cup-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}

@media (max-width: 700px) {
    .water-stats-row {
        grid-template-columns: 1fr;
    }

    .water-cup-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

/* Final sidebar-header alignment */
header[data-testid="stHeader"] {
    min-height: 2.5rem !important;
    height: 2.5rem !important;
}

section[data-testid="stSidebar"]::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2.5rem;
    background: #0B1014;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    z-index: 2;
    pointer-events: none;
}

section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    position: relative !important;
    z-index: 3 !important;
    width: 100% !important;
    min-height: 2.5rem !important;
    height: 2.5rem !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}

/* Sidebar navigation: fixed icon column + fixed text column */
.nav-align-marker {
    display: none !important;
}

section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-align-marker) {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-align-marker) + [data-testid="stElementContainer"] .stButton > button {
    display: grid !important;
    grid-template-columns: 1.35rem minmax(0, 1fr) !important;
    column-gap: 0.72rem !important;
    align-items: center !important;
    justify-content: stretch !important;
    text-align: left !important;
    padding-left: 0.95rem !important;
    padding-right: 0.95rem !important;
}

section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-align-marker) + [data-testid="stElementContainer"] .stButton > button::before {
    grid-column: 1 !important;
    width: 1.35rem !important;
    min-width: 1.35rem !important;
    text-align: center !important;
    color: currentColor !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    line-height: 1 !important;
}

section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-align-marker) + [data-testid="stElementContainer"] .stButton > button > div,
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-align-marker) + [data-testid="stElementContainer"] .stButton > button p {
    grid-column: 2 !important;
    width: 100% !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: left !important;
    white-space: nowrap !important;
}

section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-checkin-marker) + [data-testid="stElementContainer"] .stButton > button::before { content: "⌂"; }
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-water-marker) + [data-testid="stElementContainer"] .stButton > button::before { content: "≋"; }
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-history-marker) + [data-testid="stElementContainer"] .stButton > button::before { content: "▥"; }
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-insights-marker) + [data-testid="stElementContainer"] .stButton > button::before { content: "✦"; }
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-guide-marker) + [data-testid="stElementContainer"] .stButton > button::before { content: "◈"; }
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-settings-marker) + [data-testid="stElementContainer"] .stButton > button::before { content: "⚙"; }

/* Keep the water symbol white like the other inactive navigation icons. */
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.nav-water-marker) + [data-testid="stElementContainer"] .stButton > button[kind="secondary"]::before {
    color: #FFFFFF !important;
}

/* Water page: one clean control panel, no nested/overlapping card outlines */
.water-page-intro {
    margin-left: 1.15rem !important;
    margin-right: 1.15rem !important;
}

.water-summary-card {
    padding: 1.2rem 1.35rem !important;
}

.water-cup-board {
    padding: 1.3rem 1.35rem !important;
    min-height: 470px !important;
}

.water-board-heading,
.water-board-sub {
    padding-left: 0.05rem;
    padding-right: 0.05rem;
}

.water-control-column-marker {
    display: none !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="column"]:has(.water-control-column-marker) > div {
    min-height: 470px !important;
    height: 100% !important;
    padding: 1.3rem 1.35rem !important;
    background: rgba(255, 250, 242, 0.97) !important;
    border: 1px solid #D7C8B6 !important;
    border-radius: 19px !important;
    box-shadow: 0 8px 22px rgba(58, 59, 50, 0.08) !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="column"]:has(.water-control-column-marker) [data-testid="stVerticalBlock"] {
    gap: 0.78rem !important;
}

.water-control-card {
    margin: 0 0 0.15rem 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: 0 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
}

.water-control-title {
    margin: 0 !important;
    padding: 0 !important;
}

.water-control-copy {
    margin: 0.35rem 0 0.35rem 0 !important;
    padding: 0 !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="column"]:has(.water-control-column-marker) [data-testid="stButton"] {
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="column"]:has(.water-control-column-marker) [data-testid="stButton"] > button {
    margin: 0 !important;
    min-height: 48px !important;
    height: 48px !important;
    box-shadow: none !important;
}

.water-next-card,
.water-goal-card {
    margin-top: 0.15rem !important;
}


section[data-testid="stSidebar"] .st-key-nav_Water button p,
section[data-testid="stSidebar"] [class*="st-key-nav_Water"] button p {
    transform: translateX(0) !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.water-control-shell-marker) {
    min-height: 486px !important;
    height: auto !important;
    padding: 0 !important;
    background: rgba(255, 250, 242, 0.97) !important;
    border: 1px solid #D7C8B6 !important;
    border-radius: 19px !important;
    box-shadow: 0 8px 22px rgba(58, 59, 50, 0.08) !important;
    overflow: hidden !important;
    box-sizing: border-box !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.water-control-shell-marker) div[data-testid="stVerticalBlock"] {
    padding: 1.3rem 1.35rem 1.45rem 1.35rem !important;
    gap: 0.78rem !important;
    box-sizing: border-box !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.water-control-shell-marker) .water-control-card {
    margin: 0 0 0.1rem 0 !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.water-control-shell-marker) .water-control-copy {
    margin: 0.35rem 0 0.45rem 0 !important;
    padding-right: 0.2rem !important;
}

[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.water-control-shell-marker) .water-next-card,
[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.water-control-shell-marker) .water-goal-card {
    width: 100% !important;
    box-sizing: border-box !important;
}



/* ===== FINAL UI STABILITY FIXES =====
   Keep these at the end so they override older component-specific rules. */

/* 1) Warning checkbox: vertically center the square with its label text. */
div[data-testid="stCheckbox"] label {
    display: flex !important;
    align-items: center !important;
    gap: 0.55rem !important;
    min-height: 32px !important;
    padding: 0 !important;
    margin: 0 !important;
}

div[data-testid="stCheckbox"] label > *:has(input[type="checkbox"]),
div[data-testid="stCheckbox"] label > span:first-child,
div[data-testid="stCheckbox"] label > div:first-child {
    position: static !important;
    top: auto !important;
    transform: none !important;
    align-self: center !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

div[data-testid="stCheckbox"] label p {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.25 !important;
}

/* Extra guard for Streamlit/BaseWeb checkbox DOM variants. */
div[data-testid="stCheckbox"] input[type="checkbox"] + div,
div[data-testid="stCheckbox"] input[type="checkbox"] ~ div {
    position: relative !important;
    top: -1px !important;
}

/* 2) ALL select/dropdown controls: light field + dark readable text. */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
    background: #FFFCF7 !important;
    color: #173F46 !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
div[data-testid="stSelectbox"] div[data-baseweb="select"] p,
div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
div[data-testid="stMultiSelect"] div[data-baseweb="select"] span,
div[data-testid="stMultiSelect"] div[data-baseweb="select"] p,
div[data-testid="stMultiSelect"] div[data-baseweb="select"] div {
    color: #173F46 !important;
}

/* ALL opened dropdown menus, regardless of whether Streamlit renders
   each option as an li or div. */
div[data-baseweb="popover"] [role="listbox"],
div[role="listbox"] {
    background: #FFF8EF !important;
    color: #173F46 !important;
}

div[data-baseweb="popover"] [role="option"],
div[role="listbox"] [role="option"],
li[role="option"],
div[role="option"] {
    background: #FFF8EF !important;
    color: #173F46 !important;
}

div[data-baseweb="popover"] [role="option"] *,
div[role="listbox"] [role="option"] *,
li[role="option"] *,
div[role="option"] * {
    color: #173F46 !important;
    opacity: 1 !important;
}

div[data-baseweb="popover"] [role="option"]:hover,
div[role="listbox"] [role="option"]:hover,
li[role="option"]:hover,
div[role="option"]:hover {
    background: #EEE1D0 !important;
}

div[data-baseweb="popover"] [role="option"][aria-selected="true"],
div[role="listbox"] [role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"],
div[role="option"][aria-selected="true"] {
    background: #D7E9E6 !important;
    color: #173F46 !important;
}

/* 3) Keep Streamlit Material-symbol ligatures as icons everywhere.
   The app-wide Poppins rule can otherwise render names like arrow_down,
   visibility, close, etc. as literal text. The Material Symbols font is
   explicitly imported above so this is not dependent on Streamlit's own
   font loading. */
span[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"] *,
.material-symbols-rounded,
.material-symbols-outlined,
span[class*="material-symbols"],
[class*="material-symbols"] {
    font-family: "Material Symbols Rounded" !important;
    font-weight: normal !important;
    font-style: normal !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
    -webkit-font-feature-settings: "liga" !important;
    font-feature-settings: "liga" 1 !important;
    font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24 !important;
    -webkit-font-smoothing: antialiased !important;
    text-rendering: optimizeLegibility !important;
}

/* Extra safety for expanders: never allow the long ligature name to
   stretch across the header. Even if a browser delays the icon font,
   the header gets a CSS chevron instead of visible text such as
   "arrow_down" or "keyboard_arrow_down". */
div[data-testid="stExpander"] summary [data-testid="stIconMaterial"],
div[data-testid="stExpander"] summary span[class*="material-symbols"] {
    font-size: 0 !important;
    width: 18px !important;
    min-width: 18px !important;
    height: 18px !important;
    display: inline-block !important;
    position: relative !important;
    overflow: visible !important;
    flex: 0 0 18px !important;
}

div[data-testid="stExpander"] summary [data-testid="stIconMaterial"]::after,
div[data-testid="stExpander"] summary span[class*="material-symbols"]::after {
    content: "" !important;
    position: absolute !important;
    left: 5px !important;
    top: 4px !important;
    width: 7px !important;
    height: 7px !important;
    border-right: 2px solid currentColor !important;
    border-bottom: 2px solid currentColor !important;
    transform: rotate(45deg) !important;
    transform-origin: center !important;
}

div[data-testid="stExpander"] details[open] summary [data-testid="stIconMaterial"]::after,
div[data-testid="stExpander"] details[open] summary span[class*="material-symbols"]::after {
    top: 7px !important;
    transform: rotate(225deg) !important;
}

/* ===== CHECKBOX + LEGIBILITY FIXES ===== */
/* Keep the checkbox row vertically centered, then move only the actual
   visible square slightly upward. This avoids shifting the label text. */
div[data-testid="stCheckbox"] label {
    display: flex !important;
    align-items: center !important;
    gap: 0.55rem !important;
}

/* Reset any older wrapper offsets so they cannot fight this final rule. */
div[data-testid="stCheckbox"] label > span:first-child,
div[data-testid="stCheckbox"] label > div:first-child,
div[data-testid="stCheckbox"] label > *:has(input[type="checkbox"]) {
    position: static !important;
    top: auto !important;
    transform: none !important;
    align-self: center !important;
    margin: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

/* Streamlit/BaseWeb puts the visible checkbox square next to the hidden input.
   Move that square only; do not move the text or the whole control wrapper. */
div[data-testid="stCheckbox"] input[type="checkbox"] + div,
div[data-testid="stCheckbox"] label span:has(input[type="checkbox"]) > div,
div[data-testid="stCheckbox"] label div:has(> input[type="checkbox"]) > div {
    position: relative !important;
    top: auto !important;
    transform: translateY(-4px) !important;
    margin: 0 !important;
}

div[data-testid="stCheckbox"] label p,
div[data-testid="stCheckbox"] label [data-testid="stWidgetLabel"] {
    position: static !important;
    top: auto !important;
    transform: none !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

/* Make helper/caption copy readable over the photo background. */
[data-testid="stCaptionContainer"] p {
    color: #111111 !important;
    opacity: 1 !important;
}

/* The empty-state copy in the right-side readiness/fuel/recovery cards. */
.empty-state,
.empty-state.compact {
    color: #111111 !important;
    opacity: 1 !important;
}

</style>
""", unsafe_allow_html=True)

SCOPES = ["https://www.googleapis.com/auth/calendar.events.readonly"]
REDIRECT_URI = "https://fuel-athlete-cn7ftxcdmnrlemk25camwp.streamlit.app/"
TOKEN_FILE = "/tmp/fuelcoach_token.json"
STATE_FILE = "/tmp/fuelcoach_oauth_state.txt"
USDA_API_KEY = os.environ.get("USDA_API_KEY")
FATSECRET_CONSUMER_KEY = os.environ.get("FATSECRET_CONSUMER_KEY")
FATSECRET_CONSUMER_SECRET = os.environ.get("FATSECRET_CONSUMER_SECRET")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


class ResetStorage:
    def __init__(self, path):
        self.path = path

    def _load(self):
        if not os.path.isfile(self.path):
            return {}

        try:
            with open(self.path, "r") as file:
                return json.load(file)
        except Exception:
            return {}

    def get_item(self, key):
        return self._load().get(key)

    def set_item(self, key, value):
        data = self._load()
        data[key] = value

        with open(self.path, "w") as file:
            json.dump(data, file)

    def remove_item(self, key):
        data = self._load()
        data.pop(key, None)

        with open(self.path, "w") as file:
            json.dump(data, file)


def get_reset_client(reset_id):
    path = f"/tmp/fuelcoach_reset_{reset_id}.json"
    storage = ResetStorage(path)

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
        options=ClientOptions(
            storage=storage,
            flow_type="pkce"
        )
    )


def show_implicit_password_reset():
    app_url = json.dumps(REDIRECT_URI)
    supabase_url = json.dumps(SUPABASE_URL)
    supabase_key = json.dumps(SUPABASE_KEY)

    st.markdown("""
    <div class="login-hero">
        <div class="login-badge">⚡ FUEL COACH</div>
        <div class="login-title">Choose a new password</div>
        <div class="login-text">Enter your new password below.</div>
    </div>
    """, unsafe_allow_html=True)

    reset_col1, reset_col2, reset_col3 = st.columns([1, 1.15, 1])

    with reset_col2:
        components.html(
            f"""
            <!doctype html>
            <html>
            <head>
                <meta charset="utf-8">
                <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
                <style>
                    * {{ box-sizing: border-box; }}
                    body {{
                        margin: 0;
                        padding: 0;
                        background: transparent;
                        color: #173F46;
                        font-family: Arial, sans-serif;
                    }}
                    .reset-card {{
                        background: #FFFAF2;
                        border: 1px solid #D8C8B5;
                        border-radius: 17px;
                        padding: 20px;
                        box-shadow: 0 8px 24px rgba(58, 59, 50, 0.11);
                    }}
                    label {{
                        display: block;
                        margin: 0 0 7px 2px;
                        color: #31555C;
                        font-size: 13px;
                        font-weight: 600;
                    }}
                    input {{
                        width: 100%;
                        height: 50px;
                        margin-bottom: 16px;
                        padding: 0 14px;
                        border: 1px solid #CBBCA9;
                        border-radius: 10px;
                        background: #FFFCF7;
                        color: #173F46;
                        font-size: 15px;
                        outline: none;
                    }}
                    input:focus {{
                        border-color: #4B9397;
                        box-shadow: 0 0 0 1px #4B9397;
                    }}
                    button {{
                        width: 100%;
                        height: 48px;
                        border: 1px solid #397E84;
                        border-radius: 10px;
                        background: linear-gradient(90deg, #397E84 0%, #4C9698 100%);
                        color: #FFF9F0;
                        font-size: 15px;
                        font-weight: 700;
                        cursor: pointer;
                    }}
                    button:disabled {{
                        opacity: 0.65;
                        cursor: default;
                    }}
                    .message {{
                        display: none;
                        margin-bottom: 14px;
                        padding: 10px 12px;
                        border-radius: 9px;
                        font-size: 13px;
                        line-height: 1.4;
                    }}
                    .error {{
                        display: block;
                        background: #F7E1DE;
                        color: #7A3434;
                        border: 1px solid #E6C0BB;
                    }}
                

</style>
            </head>
            <body>
                <div class="reset-card">
                    <div id="message" class="message"></div>
                    <form id="reset-form">
                        <label for="new-password">New password</label>
                        <input id="new-password" type="password" minlength="6" required>
                        <label for="confirm-password">Confirm new password</label>
                        <input id="confirm-password" type="password" minlength="6" required>
                        <button id="update-button" type="submit">Update password</button>
                    </form>
                </div>

                <script>
                    const appUrl = {app_url};
                    const supabaseUrl = {supabase_url};
                    const supabaseKey = {supabase_key};
                    const hash = new URLSearchParams(window.parent.location.hash.substring(1));
                    const accessToken = hash.get('access_token');
                    const refreshToken = hash.get('refresh_token');
                    const recoveryType = hash.get('type');
                    const message = document.getElementById('message');
                    const form = document.getElementById('reset-form');
                    const button = document.getElementById('update-button');
                    const client = window.supabase.createClient(supabaseUrl, supabaseKey);

                    function showError(text) {{
                        message.textContent = text;
                        message.className = 'message error';
                    }}

                    async function prepareRecovery() {{
                        if (recoveryType !== 'recovery' || !accessToken || !refreshToken) {{
                            form.style.display = 'none';
                            showError('This password reset link is invalid or has expired. Send yourself a new reset link.');
                            return;
                        }}

                        const {{ error }} = await client.auth.setSession({{
                            access_token: accessToken,
                            refresh_token: refreshToken
                        }});

                        if (error) {{
                            form.style.display = 'none';
                            showError('This password reset link is invalid or has expired. Send yourself a new reset link.');
                        }}
                    }}

                    form.addEventListener('submit', async function(event) {{
                        event.preventDefault();

                        const newPassword = document.getElementById('new-password').value;
                        const confirmPassword = document.getElementById('confirm-password').value;

                        if (newPassword.length < 6) {{
                            showError('Password must be at least 6 characters.');
                            return;
                        }}

                        if (newPassword !== confirmPassword) {{
                            showError('The passwords do not match.');
                            return;
                        }}

                        button.disabled = true;
                        button.textContent = 'Updating...';

                        const {{ error }} = await client.auth.updateUser({{
                            password: newPassword
                        }});

                        if (error) {{
                            button.disabled = false;
                            button.textContent = 'Update password';
                            showError('Could not update your password. Send yourself a new reset link and try again.');
                            return;
                        }}

                        await client.auth.signOut({{ scope: 'local' }});
                        window.parent.history.replaceState({{}}, '', appUrl);
                        window.parent.location.href = appUrl + '?password_reset=success';
                    }});

                    prepareRecovery();
                </script>
            </body>
            </html>
            """,
            height=360,
            scrolling=False
        )


def fatsecret_oauth1_get(url, api_params):
    if not FATSECRET_CONSUMER_KEY or not FATSECRET_CONSUMER_SECRET:
        raise ValueError("FatSecret OAuth 1.0 credentials are missing")

    oauth_params = {
        "oauth_consumer_key": FATSECRET_CONSUMER_KEY,
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_version": "1.0"
    }

    params = {**api_params, **oauth_params}

    def encode(value):
        return quote(str(value), safe="~-._")

    encoded_pairs = sorted((encode(key), encode(value)) for key, value in params.items())
    normalized = "&".join(f"{key}={value}" for key, value in encoded_pairs)
    base_string = "&".join([
        "GET",
        encode(url),
        encode(normalized)
    ])
    signing_key = f"{encode(FATSECRET_CONSUMER_SECRET)}&"
    digest = hmac.new(
        signing_key.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha1
    ).digest()
    params["oauth_signature"] = base64.b64encode(digest).decode("utf-8")

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response

def normalize_fatsecret_food(item):
    summary = item.get("food_description", "")

    def summary_value(label):
        marker = f"{label}:"
        for part in summary.split("|"):
            part = part.strip()
            if part.lower().startswith(marker.lower()):
                value = part.split(":", 1)[1].strip().lower().replace("g", "")
                try:
                    return float(value)
                except ValueError:
                    return 0.0
        return 0.0

    food_type = item.get("food_type", "")
    brand = item.get("brand_name", "")

    return {
        "fdcId": f"fatsecret:{item.get('food_id', '')}",
        "description": item.get("food_name", "Unknown food"),
        "brandOwner": brand,
        "dataType": "Branded" if food_type.lower() == "brand" else "Generic",
        "source": "FatSecret",
        "fatsecretFoodId": item.get("food_id", ""),
        "servingDescription": summary.split(" - ", 1)[0].replace("Per ", "", 1),
        "foodNutrients": [
            {"nutrientName": "Carbohydrate", "value": summary_value("Carbs")},
            {"nutrientName": "Protein", "value": summary_value("Protein")},
            {"nutrientName": "Total lipid (fat)", "value": summary_value("Fat")}
        ]
    }


def search_fatsecret_foods(query):
    response = fatsecret_oauth1_get(
        "https://platform.fatsecret.com/rest/foods/search/v1",
        {
            "search_expression": query,
            "max_results": 15,
            "format": "json"
        }
    )
    response.raise_for_status()
    foods = response.json().get("foods", {}).get("food", [])

    if isinstance(foods, dict):
        foods = [foods]

    return [normalize_fatsecret_food(item) for item in foods]


@st.cache_data(ttl=3600, show_spinner=False)
def get_fatsecret_food_details(food_id):
    if not food_id:
        return None

    response = fatsecret_oauth1_get(
        "https://platform.fatsecret.com/rest/food/v5",
        {
            "food_id": food_id,
            "format": "json"
        }
    )
    response.raise_for_status()
    food = response.json().get("food", {})
    servings = food.get("servings", {}).get("serving", [])

    if isinstance(servings, dict):
        servings = [servings]

    if not servings:
        return None

    serving = next(
        (
            item for item in servings
            if item.get("serving_description", "").strip().lower() == "100 g"
        ),
        None
    )

    if serving is None:
        serving = next(
            (
                item for item in servings
                if str(item.get("metric_serving_unit", "")).lower() == "g"
                and str(item.get("metric_serving_amount", "")) in {"100", "100.0", "100.00", "100.000"}
            ),
            servings[0]
        )

    def number(name):
        try:
            return float(serving.get(name, 0) or 0)
        except (TypeError, ValueError):
            return 0.0

    brand = food.get("brand_name", "")
    food_type = food.get("food_type", "")

    return {
        "fdcId": f"fatsecret:{food.get('food_id', food_id)}",
        "description": food.get("food_name", "Unknown food"),
        "brandOwner": brand,
        "dataType": "Branded" if food_type.lower() == "brand" else "Generic",
        "source": "FatSecret",
        "fatsecretFoodId": food.get("food_id", food_id),
        "servingDescription": serving.get("serving_description", "serving"),
        "foodNutrients": [
            {"nutrientName": "Carbohydrate", "value": number("carbohydrate")},
            {"nutrientName": "Protein", "value": number("protein")},
            {"nutrientName": "Total lipid (fat)", "value": number("fat")}
        ]
    }


def show_fatsecret_attribution():
    st.markdown(
        '<a href="https://platform.fatsecret.com">Powered by fatsecret Platform API</a>',
        unsafe_allow_html=True
    )


def search_usda_foods(query):
    if not USDA_API_KEY:
        return []

    response = requests.get(
        "https://api.nal.usda.gov/fdc/v1/foods/search",
        params={
            "api_key": USDA_API_KEY,
            "query": query,
            "pageSize": 15
        },
        timeout=10
    )
    response.raise_for_status()
    return response.json().get("foods", [])


@st.cache_data(ttl=3600, show_spinner=False)
def search_foods(query):
    if len(query.strip()) < 2:
        return []

    try:
        fatsecret_results = search_fatsecret_foods(query)
        if fatsecret_results:
            return fatsecret_results
    except (requests.RequestException, KeyError, ValueError):
        pass

    try:
        usda_results = search_usda_foods(query)
        if usda_results:
            return usda_results
    except requests.RequestException:
        pass

    st.error("Food search is temporarily unavailable. Try again later.")
    return []


def get_nutrient(food, names):
    nutrients = food.get("foodNutrients", [])

    for nutrient in nutrients:
        nutrient_name = nutrient.get("nutrientName", "").lower()

        for name in names:
            if name.lower() in nutrient_name:
                return nutrient.get("value", 0)

    return 0


def get_macros(food):
    carbs = get_nutrient(food, ["carbohydrate"])
    protein = get_nutrient(food, ["protein"])
    fat = get_nutrient(food, ["total lipid", "total fat"])

    return carbs, protein, fat


def score_food(food, minutes):
    carbs, protein, fat = get_macros(food)

    if carbs == 0 and protein == 0 and fat == 0:
        return -100

    carbs = min(carbs, 60)
    protein = min(protein, 30)
    fat = min(fat, 25)

    if minutes <= 30:
        score = (carbs * 2) - (fat * 3) - protein
    elif minutes <= 90:
        score = (carbs * 1.5) + (protein * 0.5) - (fat * 1.5)
    else:
        score = carbs + protein - fat

    return score


def recommend_foods(foods, minutes):
    ranked = []

    for food in foods:
        score = score_food(food, minutes)
        ranked.append((score, food))

    ranked.sort(key=lambda item: item[0], reverse=True)

    return ranked[:3]


def score_recovery_food(food):
    carbs, protein, fat = get_macros(food)

    if carbs == 0 and protein == 0 and fat == 0:
        return -100

    return (carbs * 1.5) + (protein * 2) - (fat * 0.5)


def recommend_recovery_foods(foods):
    ranked = []

    for food in foods:
        score = score_recovery_food(food)
        ranked.append((score, food))

    ranked.sort(key=lambda item: item[0], reverse=True)

    return ranked[:3]


def get_recovery_reason(food):
    carbs, protein, fat = get_macros(food)

    if protein >= 15 and carbs >= 15:
        return f"{protein:.1f}g protein and {carbs:.1f}g carbs. Stronger mix of protein and carbohydrates for recovery."
    elif protein >= 10:
        return f"{protein:.1f}g protein. Provides more protein for post-workout recovery."
    else:
        return f"{carbs:.1f}g carbs and {protein:.1f}g protein. Can help replenish energy after exercise."


def get_food_reason(food, minutes):
    carbs, protein, fat = get_macros(food)

    if minutes <= 30:
        return f"{carbs:.1f}g carbs and {fat:.1f}g fat. The ranking favors more carbs and less fat when practice is close."
    elif minutes <= 90:
        return f"{carbs:.1f}g carbs and {protein:.1f}g protein. The ranking favors carbs with some protein when there is more time to digest."
    else:
        return f"{carbs:.1f}g carbs and {protein:.1f}g protein. With more time before practice, the ranking allows a more balanced option."


def get_google_flow(state=None):
    client_config = {
        "web": {
            "client_id": st.secrets["GOOGLE_CLIENT_ID"],
            "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [REDIRECT_URI]
        }
    }

    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI,
        autogenerate_code_verifier=False
    )


def connect_google():
    if os.path.isfile(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        if creds.valid:
            return creds

    if "code" in st.query_params:
        if not os.path.isfile(STATE_FILE):
            st.error("Google sign-in expired. Try connecting again.")
            st.query_params.clear()
            return None

        with open(STATE_FILE, "r") as file:
            saved_state = file.read()

        if st.query_params.get("state") != saved_state:
            st.error("Google sign-in could not be verified. Try again.")
            st.query_params.clear()
            return None

        flow = get_google_flow(saved_state)

        try:
            flow.fetch_token(
                code=st.query_params["code"],
                timeout=15
            )
        except Exception as error:
            st.error("Google sign-in failed.")
            st.write(error)
            return None

        creds = flow.credentials

        with open(TOKEN_FILE, "w") as file:
            file.write(creds.to_json())

        os.remove(STATE_FILE)
        st.query_params.clear()
        st.rerun()

    flow = get_google_flow()

    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    with open(STATE_FILE, "w") as file:
        file.write(state)

    st.link_button("Connect Google Calendar",
                   auth_url, use_container_width=True)

    return None


def get_upcoming_events(creds):
    service = build("calendar", "v3", credentials=creds)
    now = datetime.utcnow().isoformat() + "Z"

    result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=20,
        singleEvents=True,
        orderBy="startTime",
        eventTypes="default"
    ).execute()

    return result.get("items", [])


def find_workout_event(events):
    keywords = [
        "practice",
        "workout",
        "training",
        "game",
        "match",
        "meet",
        "lifting",
        "weights",
        "gym",
        "cardio",
        "strength",
        "hiit",
        "run",
        "running"
    ]

    for event in events:
        name = event.get("summary", "").lower()

        if any(word in name for word in keywords):
            return event

    return None


def calculate_score(energy, hours, food, workout):
    score = 100

    if energy == "Low":
        score = score - 25
    elif energy == "Medium":
        score = score - 10

    if food == "Full meal" and hours == 4:
        score = score - 5
    elif food == "Full meal" and (hours == 5 or hours == 6):
        score = score - 15
    elif food == "Full meal" and hours >= 7:
        score = score - 25

    if food == "Light meal" and hours == 4:
        score = score - 10
    elif food == "Light meal" and (hours == 5 or hours == 6):
        score = score - 20
    elif food == "Light meal" and hours >= 7:
        score = score - 30

    if food == "Snack" and hours == 4:
        score = score - 15
    elif food == "Snack" and (hours == 5 or hours == 6):
        score = score - 25
    elif food == "Snack" and hours >= 7:
        score = score - 35

    if workout in [
        "Cardio / Endurance",
        "Strength Training",
        "HIIT / Conditioning",
        "Game / Competition"
    ] and hours >= 4:
        score = score - 5

    return max(score, 0)


def save_checkin(workout, duration, hours, minutes, food, energy, water, score):
    response = supabase.table("checkins").insert({
        "user_id": st.session_state.user_id,
        "workout": workout,
        "duration": duration,
        "hours_since_eating": hours,
        "minutes_until_practice": minutes,
        "last_food": food,
        "energy": energy,
        "hydration": water,
        "score": score
    }).execute()

    if response.data:
        return response.data[0]["id"]

    return None


def save_feedback(feedback):
    if "last_checkin_id" not in st.session_state:
        return False

    response = (
        supabase
        .table("checkins")
        .update({"feedback": feedback})
        .eq("id", st.session_state.last_checkin_id)
        .eq("user_id", st.session_state.user_id)
        .execute()
    )

    return bool(response.data)


if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "result_score" not in st.session_state:
    st.session_state.result_score = None

water_date = datetime.now().strftime("%Y-%m-%d")

if "water_goal_celebrated_for" not in st.session_state:
    st.session_state.water_goal_celebrated_for = None

if "water_tracker_date" not in st.session_state or st.session_state.water_tracker_date != water_date:
    st.session_state.water_tracker_date = water_date
    st.session_state.water_cups = 0
    st.session_state.water_goal_celebrated_for = None

if "password_recovery" not in st.session_state:
    st.session_state.password_recovery = False

if "password_reset_success" not in st.session_state:
    st.session_state.password_reset_success = False

reset_id = st.query_params.get("reset")
reset_code = st.query_params.get("code")

if st.query_params.get("password_reset") == "success":
    st.session_state.password_reset_success = True
    st.query_params.clear()

if reset_id and not reset_code:
    show_implicit_password_reset()
    st.stop()

if reset_id and reset_code:
    valid_reset_id = all(
        char.isalnum() or char in "-_"
        for char in reset_id
    )

    if not valid_reset_id:
        st.error("Invalid password reset link.")
        st.query_params.clear()
    else:
        try:
            reset_client = get_reset_client(reset_id)
            response = reset_client.auth.exchange_code_for_session({
                "auth_code": reset_code
            })

            st.session_state.user_id = response.user.id
            st.session_state.access_token = response.session.access_token
            st.session_state.refresh_token = response.session.refresh_token
            st.session_state.password_recovery = True

            reset_file = f"/tmp/fuelcoach_reset_{reset_id}.json"

            if os.path.isfile(reset_file):
                os.remove(reset_file)

            st.query_params.clear()
            st.rerun()

        except Exception:
            st.error("This password reset link is invalid or has expired.")
            st.query_params.clear()

if "access_token" in st.session_state and "refresh_token" in st.session_state:
    try:
        auth = supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

        st.session_state.user_id = auth.user.id
        st.session_state.access_token = auth.session.access_token
        st.session_state.refresh_token = auth.session.refresh_token

    except Exception:
        st.session_state.user_id = None

if st.session_state.password_recovery and st.session_state.user_id is not None:
    st.markdown("""
    <div class="login-hero">
        <div class="login-badge">⚡ FUEL COACH</div>
        <div class="login-title">Choose a new password</div>
        <div class="login-text">Enter your new password below.</div>
    </div>
    """, unsafe_allow_html=True)

    reset_col1, reset_col2, reset_col3 = st.columns([1, 1.15, 1])

    with reset_col2:
        with st.container(border=True):
            new_password = st.text_input(
                "New password",
                type="password",
                key="new_password"
            )

            confirm_password = st.text_input(
                "Confirm new password",
                type="password",
                key="confirm_new_password"
            )

            if st.button(
                "Update password",
                type="primary",
                use_container_width=True
            ):
                if len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_password != confirm_password:
                    st.error("The passwords do not match.")
                else:
                    try:
                        supabase.auth.update_user({
                            "password": new_password
                        })
                        supabase.auth.sign_out()

                        st.session_state.user_id = None
                        st.session_state.password_recovery = False
                        st.session_state.password_reset_success = True

                        if "access_token" in st.session_state:
                            del st.session_state.access_token

                        if "refresh_token" in st.session_state:
                            del st.session_state.refresh_token

                        st.rerun()

                    except Exception:
                        st.error(
                            "Could not update your password. Try the reset link again.")

    st.stop()

if st.session_state.user_id is None:
    st.markdown("""
    <div class="login-hero">
        <div class="login-badge">⚡ FUEL COACH</div>
        <div class="login-title">Fuel smarter. Train stronger.</div>
        <div class="login-text">A simple fueling dashboard built for teen athletes.</div>
    </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 1.15, 1])

    with auth_col2:
        if st.session_state.password_reset_success:
            st.success("Password updated. You can now log in.")
            st.session_state.password_reset_success = False

        with st.container(border=True):
            st.markdown(
                '<div class="card-kicker login-kicker">WELCOME BACK</div>', unsafe_allow_html=True)

            auth_option = st.radio(
                "Choose an option",
                ["Log in", "Sign up"],
                horizontal=True,
                label_visibility="collapsed"
            )

            email = st.text_input("Email", key="login_email")
            password = st.text_input(
                "Password", type="password", key="login_password")

            if auth_option == "Sign up":
                if st.button("Create account", type="primary", use_container_width=True):
                    try:
                        response = supabase.auth.sign_up({
                            "email": email,
                            "password": password
                        })

                        if response.session:
                            st.session_state.user_id = response.user.id
                            st.session_state.access_token = response.session.access_token
                            st.session_state.refresh_token = response.session.refresh_token
                            st.rerun()
                        else:
                            st.success("Account created. You can now log in.")

                    except Exception as error:
                        st.error("Could not create account.")
                        st.write(error)

            else:
                if st.button("Log in", type="primary", use_container_width=True):
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })

                        st.session_state.user_id = response.user.id
                        st.session_state.access_token = response.session.access_token
                        st.session_state.refresh_token = response.session.refresh_token
                        st.rerun()

                    except Exception:
                        st.error("Incorrect email or password.")

                with st.expander("Forgot password?"):
                    st.markdown(
                        '<div class="reset-help-text">Enter your email above, then send yourself a reset link.</div>',
                        unsafe_allow_html=True
                    )

                    if st.button(
                        "Send reset link",
                        key="send_reset_link",
                        use_container_width=True
                    ):
                        if not email.strip():
                            st.error("Enter your email address above first.")
                        else:
                            reset_id = secrets.token_urlsafe(18)
                            reset_client = get_reset_client(reset_id)
                            reset_url = f"{REDIRECT_URI}?reset={reset_id}"

                            try:
                                reset_client.auth.reset_password_for_email(
                                    email.strip(),
                                    {"redirect_to": reset_url}
                                )
                                st.success(
                                    "If an account exists for that email, a reset link has been sent."
                                )
                            except Exception as error:
                                st.error("Could not send the reset email.")
                                st.write(error)

        show_fatsecret_attribution()

    st.stop()

if "page" not in st.session_state:
    st.session_state.page = "Check-in"

if "selected_foods" not in st.session_state:
    st.session_state.selected_foods = []

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-wrap">
        <span class="sidebar-icon">⚡</span>
        <div class="sidebar-brand">Fuel Athlete</div>
        <div class="sidebar-sub">Fuel smart. Perform strong.</div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("Check-in", "checkin"),
        ("Water", "water"),
        ("History", "history"),
        ("Insights", "insights"),
        ("Fuel Guide", "guide"),
        ("Settings", "settings")
    ]

    for nav_name, nav_class in nav_items:
        nav_type = "primary" if st.session_state.page == nav_name else "secondary"

        st.markdown(
            f'<span class="nav-align-marker nav-{nav_class}-marker"></span>',
            unsafe_allow_html=True
        )

        if st.button(
            nav_name,
            key=f"nav_{nav_name}",
            type=nav_type,
            use_container_width=True
        ):
            if st.session_state.page != nav_name:
                st.session_state.page = nav_name
                st.rerun()

    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="side-tip">
        <div class="side-tip-title">💧 Hydration Tip</div>
        <div class="side-tip-text">Drink water 1–2 hours before practice so you start hydrated and ready to go.</div>
    </div>
    <div class="sidebar-button-gap"></div>
    """, unsafe_allow_html=True)

    if st.button("↪   Log out", key="logout_button", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.user_id = None
        st.session_state.result_score = None

        if "access_token" in st.session_state:
            del st.session_state.access_token

        if "refresh_token" in st.session_state:
            del st.session_state.refresh_token

        st.rerun()

page = st.session_state.page

today_label = datetime.now().strftime("%b %d, %Y")

st.markdown(
    f"""
    <div class="topbar">
        <div>
            <div class="topbar-brand">⚡ FUEL COACH</div>
            <div class="topbar-sub">Fuel smart. Perform strong.</div>
        </div>
        <div class="topbar-date">📅 {today_label}</div>
    </div>
    """,
    unsafe_allow_html=True
)

hero_content = {
    "Check-in": (
        "TODAY'S FUEL PLAN",
        "Ready for your next workout?",
        "Check how you feel, add the foods you have, and get a simple pre- and post-workout plan."
    ),
    "Water": (
        "DAILY HYDRATION",
        "Track your 12-cup water goal",
        "Mark each 8 oz cup you finish and celebrate when you hit your hydration goal."
    ),
    "History": (
        "YOUR PROGRESS",
        "Review your workout history",
        "See your recent readiness scores, workout details, and saved feedback in one place."
    ),
    "Insights": (
        "YOUR PATTERNS",
        "Learn what works for you",
        "Use your recent check-ins to spot trends in readiness, energy, and recovery."
    ),
    "Fuel Guide": (
        "QUICK GUIDE",
        "Fuel with better timing",
        "Use these simple reminders to plan food and hydration around training."
    ),
    "Settings": (
        "APP SETTINGS",
        "Manage your connections",
        "Update your calendar connection, current foods, and active fuel plan."
    )
}

hero_eyebrow, hero_title, hero_text = hero_content[page]

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-content">
            <div class="hero-eyebrow">{hero_eyebrow}</div>
            <div class="hero-title">{hero_title}</div>
            <div class="hero-text">{hero_text}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

try:
    history_response = (
        supabase
        .table("checkins")
        .select("*")
        .eq("user_id", st.session_state.user_id)
        .order("created_at", desc=True)
        .execute()
    )
    history = history_response.data
except Exception:
    history = []


def show_week_glance(items):
    recent_scores = items[:7][::-1]

    if recent_scores:
        week_cols = st.columns(7, gap="small")

        for index, col in enumerate(week_cols):
            with col:
                if index < len(recent_scores):
                    item = recent_scores[index]
                    date_text = item.get("created_at", "")[:10]

                    try:
                        day_text = datetime.fromisoformat(
                            date_text).strftime("%a")
                    except Exception:
                        day_text = "Day"

                    value = item.get("score", 0) or 0
                    st.markdown(
                        f"""
                        <div class="week-cell">
                            <div class="week-day">{day_text}</div>
                            <div class="week-score">{value}</div>
                            <div class="week-bar"><span style="width:{value}%"></span></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div class="week-cell muted"><div class="week-day">—</div><div class="week-score">—</div><div class="week-bar"><span style="width:0%"></span></div></div>',
                        unsafe_allow_html=True
                    )
    else:
        st.markdown(
            '<div class="empty-state compact">Your recent readiness scores will build here as you use Fuel Coach.</div>',
            unsafe_allow_html=True
        )


def show_recent_insight(items):
    if len(items) >= 3:
        recent = items[:5]
        great_count = sum(
            1 for item in recent if item.get("feedback") == "Great")
        low_count = sum(1 for item in recent if item.get("feedback") == "Low")

        if great_count >= 3:
            st.success(
                "Your energy has felt strong in most of your recent workouts. Your current fueling routine seems to be working well."
            )
        elif low_count >= 2:
            st.warning(
                "You've reported low energy in multiple recent workouts. Consider eating a little earlier or choosing a stronger pre-workout fuel option."
            )
        else:
            st.info(
                "Your recent workout energy has been mixed. Keep checking in so Fuel Coach can learn more about what works for you."
            )
    else:
        st.info("Complete at least 3 workouts to unlock a recent fueling insight.")


def history_rows(items):
    rows = []

    for item in items:
        rows.append({
            "Date": item.get("created_at", "")[:10],
            "Workout": item.get("workout", ""),
            "Duration": item.get("duration", ""),
            "Energy": item.get("energy", ""),
            "Hydration": item.get("hydration", ""),
            "Score": item.get("score", ""),
            "Feedback": item.get("feedback", "") or ""
        })

    return rows


def maybe_launch_water_celebration():
    today_key = st.session_state.water_tracker_date

    if (
        st.session_state.water_cups >= 12
        and st.session_state.get("water_goal_celebrated_for") != today_key
    ):
        st.session_state.water_goal_celebrated_for = today_key
        st.balloons()


def render_water_page():
    maybe_launch_water_celebration()

    cups_done = st.session_state.water_cups
    cups_total = 12
    ounces_done = cups_done * 8
    cups_left = max(0, cups_total - cups_done)
    percent_done = int((cups_done / cups_total) * 100)

    st.markdown(
        '<div class="water-page-intro">Log water here separately from your workout fueling check-in. Each cup represents 8 oz.</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="water-summary-card">'
        f'<div class="water-summary-top">'
        f"<div><div class='water-summary-label'>TODAY'S HYDRATION</div><div class='water-summary-number'>{cups_done}<span>/ 12 cups</span></div></div>"
        f'<div class="water-summary-label">{ounces_done} OZ LOGGED</div>'
        f'</div>'
        f'<div class="water-progress-track"><div class="water-progress-fill" style="width:{percent_done}%"></div></div>'
        f'<div class="water-stats-row">'
        f'<div class="water-stat-pill"><div class="water-stat-title">Progress</div><div class="water-stat-value">{percent_done}%</div></div>'
        f'<div class="water-stat-pill"><div class="water-stat-title">Water</div><div class="water-stat-value">{ounces_done} oz</div></div>'
        f'<div class="water-stat-pill"><div class="water-stat-title">Cups left</div><div class="water-stat-value">{cups_left}</div></div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    water_left, water_right = st.columns([1.35, 0.65], gap="large")

    with water_left:
        cup_cards = []

        for i in range(cups_total):
            filled = i < cups_done
            fill_height = 54 if filled else 0
            filled_class = " filled" if filled else ""
            status = "Done ✓" if filled else "Empty"
            cup_cards.append(
                f'<div class="water-cup-card{filled_class}">'
                f'<div class="water-cup-visual"><div class="water-cup-fill" style="height:{fill_height}px"></div></div>'
                f'<div class="water-cup-number">Cup {i + 1}</div>'
                f'<div class="water-cup-status">{status}</div>'
                f'</div>'
            )

        st.markdown(
            '<div class="water-cup-board">'
            '<div class="water-board-heading">Your 12 cups</div>'
            '<div class="water-board-sub">The cups fill from left to right as you log water.</div>'
            f'<div class="water-cup-grid">{"".join(cup_cards)}</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with water_right:
        with st.container(border=True):
            st.markdown(
                '<span class="water-control-shell-marker"></span>'
                '<div class="water-control-card">'
                '<div class="water-control-title">Update your water</div>'
                '<div class="water-control-copy">Add a cup when you finish 8 oz. Drain one if you logged it by mistake.</div>'
                '</div>',
                unsafe_allow_html=True
            )

            minus_col, plus_col = st.columns(2, gap="small")

            with minus_col:
                if st.button("− Drain", key="water_page_minus", use_container_width=True, disabled=cups_done == 0):
                    st.session_state.water_cups = max(0, cups_done - 1)
                    st.rerun()

            with plus_col:
                if st.button("+ Fill", key="water_page_plus", type="primary", use_container_width=True, disabled=cups_done == 12):
                    st.session_state.water_cups = min(12, cups_done + 1)
                    st.rerun()

            if st.button("Reset today", key="water_page_reset", use_container_width=True, disabled=cups_done == 0):
                st.session_state.water_cups = 0
                st.session_state.water_goal_celebrated_for = None
                st.rerun()

            if cups_done >= cups_total:
                st.markdown(
                    f'<div class="water-goal-card">'
                    f'<div class="water-goal-badge">🏆</div>'
                    f'<div class="water-goal-title">Goal complete!</div>'
                    f'<div class="water-goal-text">All 12 cups are filled — {ounces_done} oz logged today.</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                next_cup = cups_done + 1
                plural = "cup" if cups_left == 1 else "cups"
                st.markdown(
                    f'<div class="water-next-card"><b>Next:</b> fill Cup {next_cup} after your next 8 oz. You have {cups_left} {plural} left today.</div>',
                    unsafe_allow_html=True
                )


if page == "Check-in":
    main_left, main_right = st.columns([1, 1], gap="large")

    with main_left:
        with st.container(border=True):
            st.markdown(
                '<div class="section-title"><span class="section-number teal">1</span>YOUR CHECK-IN</div>',
                unsafe_allow_html=True
            )

            energy = st.radio(
                "Energy level",
                ["High", "Medium", "Low"],
                horizontal=True,
                key="energy_radio"
            )

            hours = st.number_input(
                "Hours since you last ate",
                min_value=0,
                max_value=8,
                value=4,
                step=1
            )

            food = st.selectbox(
                "Last meal",
                ["Full meal", "Light meal", "Snack"]
            )

            water = st.radio(
                "Hydration",
                ["Well hydrated", "A little thirsty", "Very thirsty"],
                horizontal=True,
                key="hydration_radio"
            )

            avoid = st.multiselect(
                "Dietary restrictions",
                ["Dairy-free", "Nut-free", "Gluten-free", "Vegetarian"]
            )

            if avoid:
                st.caption(
                    "Only add foods you know meet your dietary needs. Always check the label or ingredients."
                )

            warning = st.checkbox("I feel dizzy, faint, confused, or sick")

        with st.container(border=True):
            st.markdown(
                '<div class="section-title"><span class="section-number blue">2</span>YOUR WORKOUT</div>',
                unsafe_allow_html=True
            )

            workout = st.selectbox(
                "Workout type",
                [
                    "Light / Recovery Workout",
                    "Cardio / Endurance",
                    "Strength Training",
                    "Team / Sport Practice",
                    "HIIT / Conditioning",
                    "Game / Competition"
                ]
            )

            google_creds = connect_google()
            calendar_minutes = None
            calendar_duration = None

            if google_creds:
                events = get_upcoming_events(google_creds)
                timed_events = [
                    event
                    for event in events
                    if event["start"].get("dateTime")
                ]

                if timed_events:
                    guessed_event = find_workout_event(timed_events)
                    event_labels = ["Enter workout manually"]
                    default_index = 0

                    for event in timed_events:
                        name = event.get("summary", "Untitled event")
                        start = event["start"].get("dateTime")
                        start_time = datetime.fromisoformat(
                            start.replace("Z", "+00:00"))
                        label = f"{name} — {start_time.strftime('%b %d at %I:%M %p')}"
                        event_labels.append(label)

                        if guessed_event and event.get("id") == guessed_event.get("id"):
                            default_index = len(event_labels) - 1

                    selected_index = st.selectbox(
                        "Calendar workout",
                        range(len(event_labels)),
                        index=default_index,
                        format_func=lambda i: event_labels[i]
                    )

                    if selected_index != 0:
                        calendar_event = timed_events[selected_index - 1]
                        start = calendar_event["start"].get("dateTime")
                        start_time = datetime.fromisoformat(
                            start.replace("Z", "+00:00"))
                        now = datetime.now(start_time.tzinfo)
                        minutes_until = max(
                            0,
                            int((start_time - now).total_seconds() / 60)
                        )

                        if minutes_until <= 120:
                            calendar_minutes = minutes_until

                        end = calendar_event["end"].get("dateTime")

                        if end:
                            end_time = datetime.fromisoformat(
                                end.replace("Z", "+00:00"))
                            calendar_duration = int(
                                (end_time - start_time).total_seconds() / 60
                            )

            if calendar_duration is not None:
                duration = calendar_duration
                st.metric("Workout duration", f"{duration} min")
            else:
                duration = st.number_input(
                    "Workout duration (minutes)",
                    min_value=30,
                    max_value=150,
                    value=90,
                    step=15
                )

            if calendar_minutes is not None:
                minutes = calendar_minutes
                st.info(f"Calendar workout starts in {minutes} minutes.")
            else:
                minutes = st.number_input(
                    "Time until practice (minutes)",
                    min_value=0,
                    max_value=120,
                    value=60,
                    step=5
                )

        with st.container(border=True):
            st.markdown(
                '<div class="section-title"><span class="section-number sand">3</span>YOUR KITCHEN</div>',
                unsafe_allow_html=True
            )

            food_search = st.text_input("Search for a food you have")

            if food_search:
                results = search_foods(food_search)
                priority = {
                    "Generic": 1,
                    "Foundation": 1,
                    "SR Legacy": 2,
                    "Survey (FNDDS)": 3,
                    "Branded": 4
                }

                results.sort(
                    key=lambda item: priority.get(item.get("dataType", ""), 5)
                )

                if results:
                    food_options = {}

                    for item in results:
                        name = item.get("description", "Unknown food")
                        brand = item.get("brandOwner")
                        data_type = item.get("dataType", "")

                        if data_type == "Branded" and brand:
                            label = f"{name} - {brand}"
                        else:
                            label = name

                        food_options[label] = item

                    selected = st.selectbox(
                        "Choose a food",
                        ["Select a food"] + list(food_options.keys())
                    )

                    if selected != "Select a food":
                        if st.button("Add food", use_container_width=True):
                            selected_food = food_options[selected]

                            if selected_food.get("source") == "FatSecret":
                                try:
                                    detailed_food = get_fatsecret_food_details(
                                        selected_food.get("fatsecretFoodId")
                                    )
                                    if detailed_food:
                                        selected_food = detailed_food
                                except (requests.RequestException, KeyError, ValueError):
                                    pass

                            already_added = any(
                                item["fdcId"] == selected_food["fdcId"]
                                for item in st.session_state.selected_foods
                            )

                            if not already_added:
                                st.session_state.selected_foods.append(
                                    selected_food)
                                st.rerun()
                else:
                    st.write("No foods found.")

                if results and any(
                    item.get("source") == "FatSecret" for item in results
                ):
                    show_fatsecret_attribution()

            if st.session_state.selected_foods:
                pills = "".join(
                    f'<span class="food-pill">{item["description"]}</span>'
                    for item in st.session_state.selected_foods
                )
                st.markdown(
                    f'<div class="pill-wrap">{pills}</div>', unsafe_allow_html=True)

                with st.expander("Manage foods"):
                    food_cards = []

                    for item in st.session_state.selected_foods:
                        carbs, protein, fat = get_macros(item)
                        food_cards.append(
                            f"""<div class="manage-food-card">
                                <div class="manage-food-name">{item['description']}</div>
                                <div class="manage-food-macros">
                                    <span class="manage-food-macro"><b>{carbs:.1f}g</b> carbs</span>
                                    <span class="manage-food-macro"><b>{protein:.1f}g</b> protein</span>
                                    <span class="manage-food-macro"><b>{fat:.1f}g</b> fat</span>
                                </div>
                            </div>"""
                        )

                    st.markdown(
                        f'<div class="manage-food-list">{"".join(food_cards)}</div>',
                        unsafe_allow_html=True
                    )
                    food_to_remove = st.selectbox(
                        "Remove a food",
                        ["Select a food"] + [
                            item["description"]
                            for item in st.session_state.selected_foods
                        ]
                    )

                    if food_to_remove != "Select a food":
                        if st.button("Remove food", use_container_width=True):
                            st.session_state.selected_foods = [
                                item
                                for item in st.session_state.selected_foods
                                if item["description"] != food_to_remove
                            ]
                            st.rerun()
            else:
                st.caption(
                    "Add foods you already have so Fuel Coach can rank your options.")

            check = st.button(
                "See My Fuel Plan →",
                type="primary",
                use_container_width=True
            )

    if check:
        if warning:
            st.error(
                "Don't start the workout yet. Tell a parent, coach, trainer, or nurse how you're feeling."
            )
        else:
            score = calculate_score(energy, hours, food, workout)
            st.session_state.last_checkin_id = save_checkin(
                workout,
                duration,
                hours,
                minutes,
                food,
                energy,
                water,
                score
            )
            st.session_state.result_score = score
            st.session_state.result_minutes = minutes
            st.session_state.result_water = water

    with main_right:
        with st.container(border=True):
            st.markdown(
                '<div class="right-title">↗ &nbsp; FUEL READINESS</div>',
                unsafe_allow_html=True
            )

            if st.session_state.result_score is None:
                st.markdown(
                    '<div class="empty-state compact">Complete your check-in to see your readiness score and fuel plan.</div>',
                    unsafe_allow_html=True
                )
            else:
                score = st.session_state.result_score
                result_minutes = st.session_state.get(
                    "result_minutes", minutes)
                result_water = st.session_state.get("result_water", water)

                if score >= 85:
                    status = "READY"
                    message = "You're in a good spot for practice."
                elif score >= 70:
                    status = "GOOD"
                    message = "A little more fuel would probably help you perform your best."
                else:
                    status = "LOW"
                    message = "You probably need more fuel before practice."

                gauge_col, message_col = st.columns([0.9, 1.1], gap="medium")

                with gauge_col:
                    degrees = score * 3.6
                    st.markdown(
                        f"""
                        <div class="gauge-wrap">
                            <div class="gauge" style="background: conic-gradient(#3E8D92 {degrees}deg, #DDD8CD 0deg);">
                                <div class="gauge-inner">
                                    <div class="gauge-score">{score}</div>
                                    <div class="gauge-status">{status}</div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with message_col:
                    st.markdown(
                        f'<div class="readiness-message">{message}</div>',
                        unsafe_allow_html=True
                    )
                    st.progress(score)
                    st.caption(f"Readiness {score}/100")

                if result_water == "A little thirsty":
                    st.info("Have some water before you start.")
                elif result_water == "Very thirsty":
                    st.warning("Take some time to rehydrate before starting.")

                if score < 70 and result_minutes <= 15:
                    st.write(
                        "If you still feel low on energy, let your coach know before starting."
                    )

        with st.container(border=True):
            st.markdown(
                '<div class="right-title">★ &nbsp; BEST FUEL RIGHT NOW</div>',
                unsafe_allow_html=True
            )

            if st.session_state.result_score is None:
                st.markdown(
                    '<div class="empty-state compact">Your top food choices will appear here after your readiness check.</div>',
                    unsafe_allow_html=True
                )
            elif st.session_state.selected_foods:
                result_minutes = st.session_state.get(
                    "result_minutes", minutes)
                recommendations = recommend_foods(
                    st.session_state.selected_foods,
                    result_minutes
                )

                if recommendations:
                    top_score, top_food = recommendations[0]
                    top_reason = get_food_reason(top_food, result_minutes)
                    st.markdown(
                        f"""
                        <div class="featured-food">
                            <div class="featured-icon">⚡</div>
                            <div>
                                <div class="featured-label">TOP PICK</div>
                                <div class="featured-name">{top_food['description']}</div>
                                <div class="featured-reason">{top_reason}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    other = recommendations[1:]

                    if other:
                        st.markdown(
                            '<div class="mini-label">OTHER GOOD OPTIONS</div>',
                            unsafe_allow_html=True
                        )
                        other_cols = st.columns(len(other), gap="small")

                        for col, item in zip(other_cols, other):
                            score_value, recommended_food = item

                            with col:
                                st.markdown(
                                    f'<div class="mini-food">{recommended_food["description"]}</div>',
                                    unsafe_allow_html=True
                                )

                    if any(
                        food.get("source") == "FatSecret"
                        for _, food in recommendations
                    ):
                        show_fatsecret_attribution()
            else:
                st.info("Add foods in Your Kitchen to get recommendations.")

        with st.container(border=True):
            st.markdown(
                '<div class="right-title">✚ &nbsp; AFTER YOUR WORKOUT</div>',
                unsafe_allow_html=True
            )

            if st.session_state.result_score is None:
                st.markdown(
                    '<div class="empty-state compact">Recovery options will appear here with your fuel plan.</div>',
                    unsafe_allow_html=True
                )
            elif st.session_state.selected_foods:
                recovery_foods = recommend_recovery_foods(
                    st.session_state.selected_foods
                )

                st.markdown(
                    '<div class="recovery-copy">Focus on recovery and replenish your body after training.</div>',
                    unsafe_allow_html=True
                )

                for score_value, recommended_food in recovery_foods:
                    st.markdown(
                        f'<div class="recovery-row">✓ {recommended_food["description"]}</div>',
                        unsafe_allow_html=True
                    )

                if any(
                    food.get("source") == "FatSecret"
                    for _, food in recovery_foods
                ):
                    show_fatsecret_attribution()

                st.caption(
                    "For food allergies or dietary restrictions, always check the food label or ingredients."
                )
            else:
                st.info("Add foods in Your Kitchen to get recovery recommendations.")

    with st.container(border=True):
        st.markdown(
            '<div class="week-title">▥ &nbsp; YOUR WEEK AT A GLANCE</div>',
            unsafe_allow_html=True
        )
        show_week_glance(history)

    bottom_left, bottom_right = st.columns([0.8, 1.2], gap="large")

    with bottom_left:
        with st.container(border=True):
            st.markdown(
                '<div class="card-kicker">POST-WORKOUT CHECK-IN</div>',
                unsafe_allow_html=True
            )

            feedback = st.selectbox(
                "How did your energy feel during the workout?",
                ["Select an answer", "Great", "Okay", "Low"]
            )

            if feedback != "Select an answer":
                if st.button("Save feedback", use_container_width=True):
                    if save_feedback(feedback):
                        st.success("Feedback saved.")
                    else:
                        st.error(
                            "Complete a readiness check before saving feedback.")

    with bottom_right:
        with st.container(border=True):
            st.markdown(
                '<div class="card-kicker">RECENT INSIGHT</div>',
                unsafe_allow_html=True
            )
            show_recent_insight(history)

elif page == "Water":
    render_water_page()

elif page == "History":
    with st.container(border=True):
        st.markdown(
            '<div class="week-title">▥ &nbsp; YOUR WEEK AT A GLANCE</div>', unsafe_allow_html=True)
        show_week_glance(history)

    with st.container(border=True):
        st.markdown(
            '<div class="page-heading">Full check-in history</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="page-subheading">Every row belongs only to your signed-in account.</div>',
            unsafe_allow_html=True
        )

        if history:
            st.dataframe(
                history_rows(history),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(
                "No check-ins yet. Complete a readiness check to start your history.")

elif page == "Insights":
    scores = [item.get("score", 0) or 0 for item in history]
    average_score = round(sum(scores) / len(scores)) if scores else 0
    best_score = max(scores) if scores else 0
    latest_score = scores[0] if scores else 0

    metric1, metric2, metric3, metric4 = st.columns(4, gap="medium")

    insight_metrics = [
        (metric1, "checkins", "▥", "Check-ins", len(history)),
        (metric2, "average", "↗", "Average readiness", average_score),
        (metric3, "best", "★", "Best readiness", best_score),
        (metric4, "latest", "⚡", "Latest readiness", latest_score)
    ]

    for metric_col, metric_class, metric_icon, metric_label, metric_value in insight_metrics:
        with metric_col:
            st.markdown(
                f"""
                <div class="insight-metric-card {metric_class}">
                    <div class="insight-metric-top">
                        <div class="insight-metric-label">{metric_label}</div>
                        <div class="insight-metric-icon">{metric_icon}</div>
                    </div>
                    <div class="insight-metric-value">{metric_value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    insight_left, insight_right = st.columns([1, 1], gap="large")

    with insight_left:
        with st.container(border=True):
            st.markdown(
                '<div class="card-kicker">RECENT FUELING PATTERN</div>', unsafe_allow_html=True)
            show_recent_insight(history)

    with insight_right:
        with st.container(border=True):
            st.markdown(
                '<div class="card-kicker">ENERGY FEEDBACK</div>', unsafe_allow_html=True)

            great_count = sum(
                1 for item in history if item.get("feedback") == "Great")
            okay_count = sum(
                1 for item in history if item.get("feedback") == "Okay")
            low_count = sum(
                1 for item in history if item.get("feedback") == "Low")

            st.markdown(
                f"""
                <div class="feedback-grid">
                    <div class="feedback-chip great">
                        <div class="feedback-number">{great_count}</div>
                        <div class="feedback-label">Great</div>
                    </div>
                    <div class="feedback-chip okay">
                        <div class="feedback-number">{okay_count}</div>
                        <div class="feedback-label">Okay</div>
                    </div>
                    <div class="feedback-chip low">
                        <div class="feedback-number">{low_count}</div>
                        <div class="feedback-label">Low</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with st.container(border=True):
        st.markdown(
            '<div class="week-title">▥ &nbsp; RECENT READINESS</div>', unsafe_allow_html=True)
        show_week_glance(history)

elif page == "Fuel Guide":
    guide1, guide2 = st.columns(2, gap="large")

    with guide1:
        st.markdown(
            """
            <div class="guide-card quick">
                <div class="guide-icon">⚡</div>
                <div class="guide-title">Close to practice</div>
                <div class="guide-copy">When practice is close, Fuel Coach favors foods with more carbohydrates and less fat because they tend to fit a quick-fuel situation better.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="guide-card balance">
                <div class="guide-icon">🥣</div>
                <div class="guide-title">More time to digest</div>
                <div class="guide-copy">When there is more time before training, the app allows a more balanced choice with carbohydrates and some protein.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with guide2:
        st.markdown(
            """
            <div class="guide-card hydration">
                <div class="guide-icon">💧</div>
                <div class="guide-title">Hydration</div>
                <div class="guide-copy">Use the hydration check honestly. If you feel very thirsty, take time to drink and reassess before beginning intense activity.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="guide-card recovery">
                <div class="guide-icon">✚</div>
                <div class="guide-title">After your workout</div>
                <div class="guide-copy">Recovery recommendations give more weight to foods that combine carbohydrates and protein. Always verify labels for allergies and dietary restrictions.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.container(border=True):
        st.markdown('<div class="card-kicker">IMPORTANT</div>',
                    unsafe_allow_html=True)
        st.info(
            "Fuel Coach provides general guidance for teen athletes and is not medical advice.")

elif page == "Settings":
    settings_left, settings_right = st.columns([1, 1], gap="large")

    with settings_left:
        with st.container(border=True):
            st.markdown(
                '<div class="card-kicker">GOOGLE CALENDAR</div>', unsafe_allow_html=True)
            google_creds = connect_google()

            if google_creds:
                st.success("Google Calendar is connected.")
            else:
                st.caption(
                    "Connect Calendar to let Fuel Coach suggest an upcoming workout automatically.")

    with settings_right:
        with st.container(border=True):
            st.markdown(
                '<div class="card-kicker">CURRENT SESSION</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="settings-row"><b>Saved foods:</b> {len(st.session_state.selected_foods)}<br><b>Readiness result:</b> {st.session_state.result_score if st.session_state.result_score is not None else "None yet"}</div>',
                unsafe_allow_html=True
            )

            if st.button("Clear selected foods", use_container_width=True):
                st.session_state.selected_foods = []
                st.rerun()

            if st.button("Reset current fuel plan", use_container_width=True):
                st.session_state.result_score = None

                if "last_checkin_id" in st.session_state:
                    del st.session_state.last_checkin_id

                st.rerun()

    with st.container(border=True):
        st.markdown('<div class="card-kicker">ACCOUNT</div>',
                    unsafe_allow_html=True)
        st.success(
            "You are signed in. Your check-ins are stored separately under your Supabase user ID.")
