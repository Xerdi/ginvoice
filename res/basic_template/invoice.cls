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

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% set geometry
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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


\RequirePackage[parfill]{parskip}
\RequirePackage[np, autolanguage]{numprint}
\RequirePackage{xfp}
\RequirePackage{fp}
\RequirePackage{calc}
\RequirePackage{longtable}
\RequirePackage[gen]{eurosym}

\RequirePackage[table]{xcolor}
\RequirePackage{colortbl}
\colorlet{headerbarcolor}{black}

\pagestyle{empty}
\linespread{1.5}
\setlength{\doublerulesep}{\arrayrulewidth}

\newcounter{hours} \newcounter{subhours} \newcounter{cost} \newcounter{subcost}
\newcounter{total} \newcounter{vat}

\setcounter{hours}{0} \setcounter{subhours}{0} \setcounter{cost}{0}
\setcounter{subcost}{0}

\newcommand{\currency}[1]{\def\@currency{#1}}
\newcommand{\vatname}[1]{\def\@vatname{#1}}
\newcommand{\vatpercent}[1]{\def\@vatpercent{#1}}
\newcommand{\serviceprice}[1]{\def\@serviceprice{#1}}

% Formats inputed number with 2 digits after the decimal place
\newcommand*{\formatNumber}[1]{\FPround{\cost}{#1}{2}\cost} %

% Returns the total of counter
\newcommand*{\total}[1]{\FPdiv{\t}{\arabic{#1}}{100}\nprounddigits{2}\np{\t}}

\newcommand{\grandtotal}{\@currency{}\total{total}}

\newcommand{\feetype}[1]{
    \textbf{#1}
    \\
}

\newcommand{\theauthor}[1]{\def\@theauthor{#1}}
\newcommand{\thetitle}[1]{\def\@thetitle{#1}}
\newcommand{\thesubtitle}[1]{\def\@thesubtitle{#1}}

\newcommand{\makeheader}{%
    \begin{center}
        \color{accent}
        {\Huge\textbf{\@thetitle} \\}
        \vspace{-.3cm}
        {\Large\textbf{\@thesubtitle} \\}
    \end{center}
}

% Create an invoice table
\newenvironment{invoiceTable}{
% Create a new row from title, unit quantity, unit rate, and unit name
    \newcommand*{\unitrow}[5]{%
        \addtocounter{cost}{\fpeval{100 * round(##4 * (\@serviceprice / 60), 2)}}%
        \addtocounter{subcost}{\fpeval{100 * round(##4 * (\@serviceprice / 60), 2)}}%
        ##1 & ##2 & ##3 & ##4 ##5 & \@currency\hfill\texttt{\nprounddigits{2}\np{\fpeval{round(##4 * (\@serviceprice / 60), 2)}}} \\
    }
    % Create a new row from title and expense amount
    \newcommand*{\feerow}[4]{%
        \addtocounter{cost}{\fpeval{100 * round(##4, 2)}}%
        \addtocounter{subcost}{\fpeval{100 * round(##4, 2)}}%
        ##1 & ##2 & ##3 & & \@currency\hfill\texttt{\nprounddigits{2}\np{##4}} \\
    }

    \newcommand{\subtotalNoStar}{%
        \setcounter{vat}{\arabic{subcost} * \@vatpercent / 100}%
        \setcounter{subcost}{\arabic{subcost} + \arabic{vat}}%
        \ifnum\@vatpercent=0{}\else{
            \textbf{\@vatname} & & & \@vatpercent\% & \textbf{\@currency\hfill\total{vat}} \\ \hline
        }\fi
        \textbf{Subtotaal} & & & \textbf{\arabic{subhours} min} & \texttt{\textbf{\@currency\hfill\total{subcost}}}%
        \setcounter{subcost}{0}%
        \setcounter{subhours}{0}%
        \\*[1.5ex]
    }
    \newcommand{\subtotalStar}{%
        \setcounter{vat}{\arabic{subcost} * \@vatpercent / 100}%
        \setcounter{subcost}{\arabic{subcost} + \arabic{vat}}%
        \ifnum\@vatpercent=0{}\else{
            \textbf{\@vatname} & & & \@vatpercent\% & {\bf\@currency\hfill\total{vat}} \\ \hline%
        }\fi
        \textbf{Subtotaal} & & & & \texttt{\textbf{\@currency\hfill\total{subcost}}}%
        \setcounter{subcost}{0}%
        \setcounter{vat}{0}%
        \\*[1.5ex]
    }
    \newcommand{\subtotal}{%
        \hline
        \@ifstar
        \subtotalStar%
        \subtotalNoStar%
    }

    % Create a new row from date and hours worked (use stored fee type and hourly rate)
    \newcommand*{\hourrow}[4]{%
        \addtocounter{hours}{##4}%
        \addtocounter{subhours}{##4}%
        \unitrow{##1}{##2}{##3}{##4}{min}%
    }
    \renewcommand{\tabcolsep}{2pt}
    \renewcommand{\extracolsep}{0pt}
    \setlength\LTcapwidth{\textwidth}
%    \setlength\LTleft{0pt}
%    \setlength\LTright{0pt}
    \begin{longtable}{p{\dimexpr0.30\linewidth-2\tabcolsep-1.25\arrayrulewidth\relax} !{\vrule width 0pt}
                      p{\dimexpr0.15\linewidth-2\tabcolsep-1.25\arrayrulewidth\relax} !{\vrule width 0pt}
                      p{\dimexpr0.42\linewidth-2\tabcolsep-1.25\arrayrulewidth\relax} !{\vrule width 0pt}
                      p{\dimexpr0.15\linewidth-2\tabcolsep-1.25\arrayrulewidth\relax} !{\vrule width 0pt}
                      p{\dimexpr0.15\linewidth-2\tabcolsep-1.25\arrayrulewidth\relax}}
        \hline
        ~
        & \textbf{Datum}
        & \textbf{Sessie omschrijving}
        & \textbf{Tijd}
        & \textbf{Bedrag} \\
        \hline
        \endhead
}{%
    \hline%
    \setcounter{vat}{\arabic{cost} * \@vatpercent / 100}%
    \setcounter{total}{\arabic{cost} + \arabic{vat}}%
    \ifnum \@vatpercent=0 \else%
        \textbf{\@vatname} & & & \@vatpercent\% & \textbf{\@currency\hfill\total{vat}} \\ \hline
    \fi
    \textbf{Totaal} & & & & \textbf{\@currency\hfill\texttt{\total{total}}} \\
\end{longtable}
}
