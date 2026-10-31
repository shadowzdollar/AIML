import pandas as pd
import numpy as np

# 1. Create a sample DataFrame
frame = pd.DataFrame({
    "a": [
        "Windows 11",
        "Ubuntu Linux",
        "Windows 10",
        "Kali Linux",
        "macOS",
        "Windows Server"
    ]
})

# 2. Identify Windows operating systems
frame["os"] = np.where(
    frame["a"].astype("string").str.contains("Windows", case=False, na=False),
    "Windows",
    "Not Windows"
)

# 3. Display the results
print(frame)


#displaying the own system

import platform

os_name = platform.system();
os_version = platform.release();


print("Os name is: ", os_name );
print("Os version is: ", os_version);