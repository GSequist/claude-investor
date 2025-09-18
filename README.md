# Pocket Gordon Gekko 

Claude with access to internet, SEC reports and metrics. Experimental application. Performs deep research for company/industry/sector news on the internet, pulls reports from SEC and calculates a set of financial ratios before generating a final comprehensive analysis, including charts. The application systematically progresses through planning, web research, regulatory filing analysis, and quantitative phases to deliver structured investment recommendations. The application is launched and controlled via CLI.

```ascii
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓███▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓███████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓▓▓▓▓██████████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓███▓▓▓▓▓▓██████████████▓▓▓▓▓▓▓▒▒▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▒▒▒▓
▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓███▓▓▓▓▓▓█▓███████████████▓▓▓▓▓▓▒▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▒▓
▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▓▓▓▓▓▓▓███████████▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒░░░░▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█▓▓▒▒▒▒░░░░░▒▒▒▒▒▒▒▒▓▓▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓▒▒▒▒░░░░░▒▒▒▒▒▒▒▒▓▓▓▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░░░░░░▒▒▒▒▒▒▒▒▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▓▒▒▒▒░░░░░▒▒▒▒▒▒▒▒▒▓▓▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒░▒▒▒▒▒▓▓▒▒▒▒▒▒▒▓▓█▓▓▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▓▓▓▒▒▒▓███████▓▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░░▒▒▒▒▒▒▒▓██▓▒▓▓▓▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░░▒▒▒░░░▒▒░░░░▒▒▓██▓▓▓▓▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒░░░░░░░▒▒▒▒▒███▓▓▓▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒░░▒▒▒▒░▒▒▒▓██▓▓▓▒▒▒▓▓▓▓▓▓▓▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▒▓▓▒▒▒▒▒▒▒▒▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒░░░░░▒▒▒▒▓▓███▓▓▓▓▒▒▒▓▓▓▓▓▓▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▒▒▓▓▒▒▒▒▒▒▒▒▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒░░░▒▒▒▒▒▒▒▒▓▓▓▓▓▓▒▒▒▒▒▒▓▓▓▓▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▒▓▓▒▒▒▒▒▒▒▒▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▓▓██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓█▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░░▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▒░▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░▒▒▒▒▒▒▒▒▓▒▓▓▓▓▓▓▓▒▒░░▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░░░▒▒▒▒▒▒▒▒▓▓▓▓▓█▓▒▒▒▒░▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓▓▓▓▒▒▒▒▒▓▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░░░░░░▒▒▒▒▒▒▓▓▓▓▓▓▒▒▒▒▒▒▒░▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░░░▒▒▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░░░░░░░░░░▒▒▒▒▒▒▒▒▒░░░░░░░▒░▒▒▒▓██▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░░▒▒▓
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓▓▓█▓▒░░░░░░░░▒▓▓▒░░░▒▒▒▓███▓▓▒▒░░░░▒▓▒▓██████▒▒▒▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒░░░▒▒▒
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░▒▓█▓█▓▒░░░░░░▒▓▓▓▓▓▓▒▒▒▓███████▓▓▒▒▒▒░▒▓▓▒▓██▓██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░▒▒
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░░░▒▓█▓▓█▓░░░░▒▒▒▒▒▒▒▒▒▒▓▓▓█████▓▒▒▒▒▒▒▒▒▒▒▒▒▓▓██▓▓██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒░░░░▒▒
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒░░░░▒░▒██▒█▓▒░░░░▒░░░▒▒▒▒▒▒▒▓████▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓█▓▓██▓▒▒▒▒▒▒▒▒▒▒▒░░░░░░░░░░▒▒
▓▓▓▓▓▓▓▓▓▓▓▓▓▒░░░░▒▒░▒▓█▓▓█▓▒░░▒▒▒▒▒▒▒▒▒▒▒▒▒▓███▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓██▒███▒▒▒▒▒▒▒▒▒░░░░░░░░░░░░▒▓
▓▓▓▓▓▓▓▓▓▓▓▓▒░░░░░░▒▒▒▓█▒▓█▓░░░░░░░░▒▒▒▒▒▒▒▓█▓██▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▓▓██▒▒▒▒▒▒▒▓▒▒▒░░░░░░░░░░▒▓
▓▓▓▓▓▓▓▓▓▓▓▒░░░░░░░▒▒▒█▓▒█▓▒░░░░░▒▒▒▒▒▒▒▒▒▓█████▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▓▒██▓▒▒▒▒▒▒▒▓▒▒▒░░░░░░░░░▒▓
▓▓▓▓▓▓▓▓▓▓▒░░░▒▒░░░▒▒▓█▓▒█▓░░░░░▒▒▒▒▒▒▒▒▒▒▓█████▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓██▒███▒▒▒▒▒▒▓▓▒▒▒░░░░░░░░░▒▓
▒▒▒▒▒▒▒▒▒▒░░░░▒▒░░░▒▒▓█▒▓▓▒░░░░▒▒▒▒▒▒▒▒▒▓▓███████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓██▓▓██▒▒▒▒▒▒▓▓▒▒▒░░░░░░░░░▒▒
░░░░░░░░░░░▒░░▒▒░░░░▒▓▓▒▓▓▒░░▒▒▒▒▒▒▒▒▒▒▒▓███▓████▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓███▓██▒▒▒▒▒▒▒▓▓▒▒▒░░░░░░░░▒▒
░░░░░░░░░░▒▒░░▒▒▒▒░░▒▓▓▒█▓░░░▒▒▒▒▒▒▒▒▒▒▒▓█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓██▒██▓▒▒▓▒▒▒▓▓▒▒▒░░░░░░░░▒▒
░░░▒▒▒░░░░▒▒░░▒▒▒▒░░▓▓▒▓▓▓░▒▒▒▒▒▒▒▒▒▒▒▒▒▓█████████▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓██▓██▓▒▓▓▒▒▒▓▓▒▒▒▒░░░░░░▒▒▒
░░░░░░░░░░▒▒░░░▒▒▒░░▓▓▒▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓███████████▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓██▓▓█▓▓▓▓▓▒▒▓▒▒▓▒▒░░░░░▒▒▒▓
░░░░░░░░░░▒▒▒░░▒▒▒░░▓▓▒▓▒▒░░▒░░░▒▒▒▒▒▒▒▓████████████▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓██▓████▓▓▒▒▒▒▒▓▒▒▒░░░░▒▒▒▓
░░░░░░░░░░▒▒▒░░▒▒▒░░▓▓▓▓▒▒░░░░░░▒▒▒▒▒▒▒▓▓███████████▓▒▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓▓▓▒▒▓███▓▒▒▒▒▒▓▓▒▒░░░▒▒▒▒▓
░░░░░░░░░░░▒▒▒░░▒▒▒▒▓▓▒▓▓░░░░░▒▒▒▒▒▒▒▒▒▓██▓▓▓████████▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒▓███▓███▓▒▒▒▒▒▓▓▒▒▒▒▒▒▒▒▒▒
░░░░░░░░░░░▒▒▒▒▒▒▒▒▒▓▓▒▓▓░░░░▒▒▒▒▒▒▒▒▒▓▓▓▓▓▓▓█████████▓▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓████████▓▒▒▒▒▒▓▓▓▒░░░░░░░░
▒▒▒▒▒▒▒░░░░▒▒▒▒▒▒▒▒▒▒▓▒▓▒░░░▒▒▒▒▒▒▒▒▒▒▓▓▓██▓▓▓▓███████▓▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓████████▓▒▒▒▒▒▓▓▓▒▒▒▒▒▒▒▒▒
▒▒▒▒▒▒░▒░░░░▒▒▒▒▒▒▒▒▒▓▒▓▒░░░░▒▒▒▒▒▒▒▒▒▓▓██▓▓▓▓▒▒██████▓▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓████████▓▒▒▒▒▒▓▓▓▒▒▒▒▒░▒▒▓
░░▒▒▒░░░░░░░▒▒▒▒▒▒▒▒▒▓▒▓▓░▒▒▒▒▒▒▒▒▒▒▒▒▓███████▓██████▓▓▒▒▒▒▒▒▒▒▒▒▓▓▓▓██████████▒▒▒▒▒▓▓▓▒▒▒░░░▒▒▓
░░░░▒░░░░░░░▒▒▓▒▒▒▒▓▒▓▒▓▓▒▒▒▒░▒▒▒▒▒▒▒▒▓███████▓██████▓▓▓▒▒▒▒▒▒▒▒▓▓▓▓███████████▓▒▒▒▒▓▓▓▒▒▒▒▒▒▒▒▓
░░░░▒░░░░░░░▒▒▓▒▒▒▒▒▒▓▓▓█▒▒▒░░▒▒▒▒▒▒▒▒▓▓█████████████▓▓▒▒▒▒▒▒▒▒▒▓▓▓▓███████████▓▒▒▒▓▓▓▓▒▒▒▒▒▒▒▒▒
```


## Features

- **Deep Financial Analysis** - Multi-phase research including web news, SEC filings, and quantitative metrics
- **AI-Powered Insights** - Claude AI provides investment recommendations with reasoning
- **Real-time Data** - Live web scraping and SEC API integration
- **Multiple Analysis Styles** - Quick, standard, or deep analysis modes
- **Interactive Charts** - Terminal-based visualizations for financial data

##Work-in-progres

This application will be further developed. Contributions are welcome.

- **Portfolio** - Persistence, memory and tracking portfolio performance over time
- **Number crunching** - Further enhance financial calculations based on fetched SEC metrics

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/GSequist/claude-investor
cd pocket-gordon-gekko
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv env

# Activate virtual environment
# On macOS/Linux:
source env/bin/activate

# On Windows:
env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Setup

The application will prompt you for required API keys on first run, or you can create a `.env` file:

```bash
# Create .env file
touch .env
```

Add the following variables to your `.env` file:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SERPAPI_KEY=your_serpapi_key_here
USER_NAME_FOR_SEC=YourCompany email@company.com
EMAIL_FOR_SEC=your-email@company.com
```

#### Required API Keys:

- **Anthropic API Key**: Get from [console.anthropic.com](https://console.anthropic.com)
- **SerpAPI Key**: Get from [serpapi.com](https://serpapi.com) for web search functionality
- **SEC API Info**: Required for SEC filings access (free, just need contact info)

## Usage

### Basic Usage

```bash
python start_.py
```

## Architecture

### Analysis Phases

1. **Planning Phase** - Creates structured research plan
2. **Web Research Phase** - Latest news and market sentiment
3. **SEC Phase** - Official filings and financial data
4. **Quantitative Phase** - Financial ratios and calculations

### Chart Types

- Line charts for trends
- Bar charts for comparisons
- Multi-line charts for multiple metrics
- Scatter plots for correlations

## Development

### Project Structure

```
pocket-gordon-gekko/
├── start_.py              # Main entry point
├── pocket_gekko.py        # Core analysis engine
├── utils/
│   ├── visualize_graph_.py    # Chart rendering
│   ├── graph_charting_.py     # Chart data generation
│   ├── visual_result_.py      # Results display
│   └── ...
├── tools/                 # Analysis tools
└── models/              # model definitions
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is for educational and research purposes only. Not financial advice. Always do your own research and consult with financial professionals before making investment decisions.

---
