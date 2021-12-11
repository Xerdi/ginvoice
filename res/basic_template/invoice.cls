% GinVoice - Creating LaTeX invoices with a GTK GUI
% Copyright (C) 2021  Erik Nijenhuis <erik@xerdi.com>
%
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
%
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
%
% You should have received a copy of the GNU General Public License
% along with this program.  If not, see <https://www.gnu.org/licenses/>.

\ProvidesClass{invoice}
\LoadClass[12pt]{article}

\RequirePackage[a4paper,hmargin=0.79in,vmargin=0.79in]{geometry}
\newlength\highlightwidth
\newlength\headerheight
\newlength\marginleft
\newlength\marginright
\newlength\margintop
\newlength\marginbottom
\setlength\highlightwidth{8cm}
\setlength\headerheight{4cm}
\setlength\marginleft{1cm}
\setlength\marginright{\marginleft}
\setlength\margintop{1cm}
\setlength\marginbottom{1cm}
\geometry{left=\marginleft,right=\marginright,top=\margintop,bottom=\marginbottom}

\NeedsTeXFormat{LaTeX2e}
\RequirePackage{hyperref}

\RequirePackage[parfill]{parskip}
\RequirePackage[np, autolanguage]{numprint}
\RequirePackage{xfp}
\RequirePackage{fp}
\RequirePackage{calc}
\RequirePackage{longtable}
\RequirePackage[gen]{eurosym}

\RequirePackage{etoolbox}

\RequirePackage[table]{xcolor}
\RequirePackage{colortbl}
\colorlet{bgcolor}{white}
\colorlet{textcolor}{black}

\pagestyle{empty}
\linespread{1.4}

\newcommand\financial[1]{\texttt{\np{#1}}}

\input{meta}

\newcommand{\makeheader}{%
    \makeatletter
    \hypersetup{
        pdftitle = {\title},
        pdfauthor = {\author},
        pdfsubject = {\subject},
        pdfkeywords = {\keywords},
        pdfproducer = {\producer},
        pdfcreator = {\creator}
    }
    \begin{center}
        \color{textcolor}
        {\Huge\textbf{\title} \\}
        \vspace{-.3cm}
        {\Large\textbf{\subtitle} \\}
    \end{center}
    \makeatother
}

\newcolumntype{L}[1]{p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{F}[1]{p{#1}}

\newcommand\cum[2]{%
    \cumoffset
    \columnheaderbgcolor
    \rowheadercolor{#1} & \currency\hfill\financial{#2} \\
}

\newcommand\rowheaderbgcolor{%
    \ifbool{styletable}{%
        \rowcolor{bgcolor}
    }{}%
}

\newcommand\columnheaderbgcolor{%
    \ifbool{styletable}{%
        \cellcolor{bgcolor}
    }{}%
}

\newcommand\rowheadercolor{%
    \ifbool{styletable}{%
        \color{textcolor}
    }{}
}

\newenvironment{invoice}[3]{%
    \ifbool{styletable}{%
        \rowcolors{2}{white}{gray!15}%
        \arrayrulecolor{textcolor}%
    }{}
    \begin{center}
        \begin{longtable}{#1}
            \rowheaderbgcolor
            #2
            \toprule
            \endfirsthead%
            \rowheaderbgcolor
            \multicolumn{\columncount}{c}{\rowheadercolor\continuationheader} \\
            \rowheaderbgcolor
            #2
            \toprule
            \endhead
            \bottomrule
            \rowheaderbgcolor
            \multicolumn{\columncount}{c}{\rowheadercolor\continuationfooter} \\
            \endfoot
            \bottomrule
%            \cline{5-5}
            #3
            \endlastfoot%
            }{
        \end{longtable}
    \end{center}
}
