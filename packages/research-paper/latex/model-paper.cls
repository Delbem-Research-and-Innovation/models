%% model-paper.cls — model Research Paper Class
%%
%% Minimal LaTeX class shared across all models in the monorepo.
%% Inherits from `article` so any standard LaTeX continues to work.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{model-paper}[2026/04/16 model Research Paper Class]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[11pt,a4paper]{article}

%% Encoding & fonts
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage{lmodern}
\RequirePackage{microtype}

%% Layout
\RequirePackage[margin=2.5cm]{geometry}
\RequirePackage{parskip}

%% Common essentials
\RequirePackage{graphicx}
\RequirePackage{booktabs}
\RequirePackage{xcolor}
\RequirePackage{amsmath,amssymb}
\RequirePackage{siunitx}
\RequirePackage{hyperref}

\hypersetup{
  colorlinks=true,
  linkcolor=black,
  citecolor=blue!50!black,
  urlcolor=blue!50!black,
}

%% Metadata helpers
\newcommand{\affiliation}[1]{\def\@affiliation{#1}}
\def\@affiliation{}

\renewcommand{\maketitle}{%
  \begin{center}
    {\LARGE\bfseries \@title\par}\vspace{0.5em}
    {\large \@author\par}
    \ifx\@affiliation\empty\else{\small \@affiliation\par}\fi
    \vspace{0.25em}{\small \@date\par}
  \end{center}
  \vspace{1em}
}
