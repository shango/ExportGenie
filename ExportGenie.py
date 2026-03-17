"""
ExportGenie.py  v11
Export Genie — Export scenes to .ma, .fbx, .abc with auto versioning.

Drag and drop this file into Maya's viewport to install.
Compatible with Maya 2025+.
"""

import datetime
import math
import os
import re
import subprocess
import sys
import shutil
import base64
import traceback
from functools import partial

import maya.cmds as cmds
import maya.mel as mel

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TOOL_NAME = "ExportGenie"
TOOL_VERSION = "v11_beta-11"
WINDOW_NAME = "multiExportWindow"
WORKSPACE_CONTROL_NAME = "exportGenieWorkspaceControl"
SHELF_BUTTON_LABEL = "ExportGenie"
ICON_FILENAME = "ExportGenie.png"

# Tab identifiers
TAB_CAMERA_TRACK = "camera_track"
TAB_MATCHMOVE = "matchmove"
TAB_FACE_TRACK = "face_track"


# Base64-encoded 32x32 RGBA PNG icon (purple-to-cyan gradient with export arrow and badge)
ICON_DATA = (
    "iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAACXBIWXMAAAsTAAALEwEAmpwYAAADKUlEQVR4nO2aWUhVURSGP83MyqB5sKigp4oGfSjSigIhyQoi04Kwt16iiYik6CEoeimIaCBooJkgqKC3CsGQBJ8aCRQbLMrANMNG8saG/8LhcK+ec+65527DDxZc9rDO/s+w91qLCwP8/8wBDgG1QBvwU9amtsPAXCxmInAb6AFiHuwuUIBlTAbeeRTgtPfANCziei+L/StL1n8Li+hIskjzTRTKapOM+YpFtLoW1wSsVd9QGWprco19jUVUamcyT2Y3kAtkqf2NrFJtuRrToTkVWEYBMFa/i4C6BK9RnfrQWOt2LTe9fdymr98Q68P6DbH/RUh3LyJMn1XkAAuBHcAFoNzRNwE46hLUrTbTF6dcc7cDC+QzEgYBa4DLQHuCu90AlLkEHZM5BZRprHt+O3AJWK1rhc5woMZHPFUPlCbwU6o+Lz7eAnuBYWGJ2KDgzm9AGD83lskSnSterBWoSkXAYOBswIunw85oTb4wocRFCxYfc9lVrc0zVT6ch4EfMRV+HD+2WEi9H8ffQn4lPgPVjtdiHLAPaAQ6ffrq8iOkOSQBPTrwxshvjg6/ZIlYzIM99SNkk48iQjIzGeESh0+zBT9P0WcnUIJPVgV4Mr9UHVmcwN984AbwO4CAbuAkMJWAmDBhOXBEC2yWU5NTfFHm9wA4od1klGPuaOAgcBqY4mgfqV3xFPAQaJEvI9BkjJ+02VwBDgArgDwixnzMxbp7XY47+kOCSvyeA+lmiApys4ClwE7gmp5QX6+JidfOK2o2T3uGdjHjM3I+hLw9O21LlELupElEA5AdpZD9aRBhvqOZRExxGoSYCn7kZCnxCUuEyXfyyRDHQxSylQyyKCQR5rwZQYZpDEGIOSgzzroQhKzEArKARykKmYQlFAaMaOMJV2RFOS/UBBDxCpiNZWQD9zwKeAHscoTmkYYkXquRja6Q4yPwTJHxHiVXcXIkqF5z+x3jgW3AS1cevhmYrsTLKvKUs5hAcL3+8XAf+JNCDWBeJrbljSnUjGMOa9F5lVHyVf7xWz3pUd5eHaTem26KlN7eBJ6oyv5d1qqN4pwyRKv+1jEAAfgH91gQ3NV/zakAAAAASUVORK5CYII=+48GgAAIABJREFUeJzt3Xm4HWWV7/HfqtpJSLJPJkYj5wRIECRh8EZEBg2TLXCvtHgJl6HjTRSEVlFxpEHpdLdto17EqftRvN3XgTmI4oA0KgmCoRXDmIhgUGYEzHimkJyqdf84IcSQYe9zqvZbtev7eZ76B5Kzf8neqbVqvW/VlgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxWKhAwB5WDFt0rg4SnYx1XbxWOMkN6WaEDoXMGyRrUrT9PlRUfzCmN3//IIt0kDoSCgnGgCU1p8O2n3s6A0bDnTXgSY/UKZpck2RtJekMYHjAa3ymLvuM7P7zdL7bP3A4o5He54PHQrFRwOA0li7f8fOqY043uRvknSEpAMl1QLHAoomlfsSRdHNMrt53LIVd5vkoUOheGgAUGjdB0yanqbpqTKdJNnrJUWhMwEl86hL36jFI75ZX/r8c6HDoDhoAFA4K2ZM6qwl6VzJTpd0QOg8QJtYb9JNSeSfmbhs9X2hwyA8GgAUgktR92snnOxm50r6K3GlD+TFTbrBoujvO5aueCh0GIRDA4Cg/nTQ7mNHDwy8W9IHJJ8aOg9QGabEpW8qSj424cE1q0LHQevRACCIZ2ZOHjO2b905Mn1C0qtC5wEq7Dm5fXz8Qyu+HToIWosGAC3lsxWvWTbxbDP7B0m7h84DYJBJN7oGzhm/bO3K0FnQGjQAaJnVr935eMV+ublmhM4CYKv+kJifMmnpqgdCB0H+aACQu9UHjp8YpfGlLp0jPnNA0a0z2Xnjlq34VuggyBcnY+RqzfSJZ8jsK5J2Dp0FQONcdtGEpSv+JXQO5IcGALlYOXPi+PhFfUWyOaGzABgac/vsuGUrLgydA/mgAUDm1hyw82GK/HpJXaGzABgec7t03LIVfxc6B7JHA4BMrTlo53e6+9dMGh06C4BsuPzvJjy46tLQOZAtGgBkwo9WrXvFpH9z2TmhswDIXJq6Zk9cuuLG0EGQHRoADNvz03etj4qS6yQ7KXQWAPlwqd8iHT3+/hW/Dp0F2aABwLD0zNht9zRKb3X5QaGzAMjdk2mUHDTxvtWrQwfB8PGFKxiy3pm7vCqJkp9T/IHK6Iw8/mroEMgGEwAMycqZE7viDfEiyfcOnQVAa7n7aRMeXLkgdA4MDw0AmrZy5sSueCD+quRvC50FQACuFTZi/f7jlnT/OXQUDB1LAGjKypkTu2oD0TclPyF0FgCBmHb2gZF/HzoGhocJABo2eOVvC11Rt8kPDp0HQFADUeQHd9y78rehg2BoaqEDoBxWzpzYFSe2UBY9a/IjQ+cBEFwtdfuMpLeHDoKhYQKAHdpU/N12NVOfS7uHzgSgGNzs0An3/vk3oXOgeUwAsF2DxT9eKGkfM93u0qzQmQAUh7m/T9K80DnQPCYA2KZNxd+0j8uWm3yKpBGhcwEolBfjmu1Vv/uFP4UOguZwFwC2avPiL8kjpf2i+AN4pVHJgL8ndAg0jwYAr7BF8Zdki112YNhUAArsrNAB0DyWAPAXVs6c2BX74Jr/xv/UbaY+dzb+Adi2KEoO7PjNqqWhc6BxTACwyVaKv0y6h+IPYEfSND41dAY0hwYAkrZe/F223CXu+QewQ8bzAEqHJQAMFn/9ZfGX5C49YBJP/APQCPf1G3ae8OCaVaGDoDFMACpuG8Vfki2m+ANogmlkfGjoEGgcDUCFbbv4q9vk00JkAlBeZtERoTOgcTwJsKJWzpzYFVtta8V/cOMfT/wD0DwmACVCA1BB2yv+Li2XRBcPYCimhg6AxtEAVMzKmRO74mjrxV+SS+oVT/wDMDRTXDIbPJeg4NgDUCE7KP6Si41/AIZjp95Dd+W5ISVBA1AROyz+g0/827eVmQC0n0RpZ+gMaAxLABWwcubErjjebvFn4x+ATERuY0JnQGOYALS5Roq/m5Y7G/8AZCCJolGhM6AxNABtrJHiL8nlbPwDkI3I05GhM6AxLAG0qZUzJ3bFtR0Wf0n6pUlHtSJTZbh9weX/FToG2ofJ3ijzD4fO0YhUTADKggagDa2cObkrrg00Uvy7TdqX+3Wy5fL/mvDrFxaEzoH2sfoNu8rK8tUt7kyWS4I3qs00Ufxl5ve4+KpfAKgiJgBtZOVRk7viZGChfMfFf/CJf3ZEWS4qSoW2GlmLVZ5H6/D5Lw3eqjbRTPEXT/wDgMqjAWgDTRZ/STzxDwCqjiWAkttU/KV9Ghznd5s0rSzTRAAbsVyHjDEBKLGNxX+RGtjw9xITG/8AAEwASmuz4r93o79n08Y/AEDl0QCU0Kbib40Xf0keufrcSrnxLzGzG919duggDWF9BXkoyxIAn//SYAmgZIZY/CXTYjcdlFOsPCWS5qZpyoN1ACBDTABKZOVRk7tqSbJIZs0Vf6nbvJQb/xKXzx2/+Pkruw/fY7aX5NIioq9GxmLF4vOPrNEAlMTKoyZ31TxZpKjJK39Jct3jVrqv+k3cB4u/JB6Egmrj848c8FaVwKbi38SGv5e4tFxWuq/6/cviDwDIHA1AwQ2n+EtyK98T/yj+ANACLAEU2MqjJnfVlDS/4e9liyUdmWWmnCVuPnf8Hdso/mXZBQ3kgc8/MsYEoKA2Ff+hXflLG5/4l2GkvG2/+AMAMkUDUEAZFH9JKtMT/yj+ANBiLAEUzMqjJnfVbHjF36XlptJs/Bu81a+R4l+WEWhZdmujXPj8I2NMAAoki+Kvcm38a7z4AwAyRQNQEBkVf2lw418ZvuqX4g8AAbEEUAArj5rcVYvSRVLTT/jbUreZpnnxR3CJu80df8ezjRf/WIOzjTKgrUbW+PwjB7xVgb1c/Id95S9J97gXfuNf88UfAJA5GoCAsiz+g1/1W/iNfxR/ACgIlgACWXnU5K5anNmVv5usV/Iib/xL3Gzu+EXDKP4lmYACueDzj4wxAQgg4+IvuS+WvMgb/4Zf/AEAmaIBaLHMi7/UbWZFfuIfxR8ACoglgBZaefzkrtpApsVfGnziX1G/6jdxZVj8yzICLf5dGCgjPv/IGBOAFsmj+Bd841+2xR8AkCkagBbI6cp/48a/Qj7xj+IPAAXHEkDOVh4/uauW+CLZsB/ys6WNX/VbuLlg4q7si3+pHoTCDBQZ4/OPHDAByNGm4p/tlb/khf2q33yKPwAgczQAOcmt+EuSFfKrfin+AFAiLAHk4OWxf/bF32Ubv+q3UGO2xE1zx/885+JfkgkokAs+/8gYDUDG8iz+ktzkRdv415riDwDIFEsAGcq5+EvF+6pfij8AlBQTgIysOnbvKbGvu12RpuT0Emsl7ZvTzx6KxN3mjP/5M9e07BXLMgIt1OoM2gaff2SMCUAG+o7d89WxrbtNrsdyexHXvZJ2y+3nNydxae7421pY/AEAmaIBGKbuE/fYdcCSWyXtI9MsuW7P+jXcbbnMivLEv8Hiz9gfAEqNJYBheOZtk8d4v98s0wGb/qNplsl+5vLjM3oZjyztc1kRNv4lbjZn/E8DXPnHKs9okbYaWePzjxzQAAyRz1fUfYeulNnrX/H/pOMl3S5ZFl/Ss9hlR2bwc4YrcfO5QYq/JM6AqDY+/8ge79QQdd85+bMynbLtX2GzTPrZsF7E1W1mRdj4l7hpzvifMvYHgHbBBGAI1v7V5LfL9ZEd/brBSYAPfRJgPvhVv2F3/yYunzv+p8+G3/BXll3QQB74/CNjTACa1H3cHgfI9R01/M/RZpkNZRJgyxV+9J+4uPIHgHbEBKAJfuK0Ud1J3zWS6k39Pul4WVOTANfgE/9Cvj+Je0Gu/F9SliugsizVolz4/CNjTACa0J32fkbSQUP73TZrcDmgIaGf+PdS8efKHwDaFA1Ag7rfsscsuX1oeD+loeWAblPQjX+JO2N/AGh3LAE0wE+cNqo77fuaMmiYNm0MtG0sB5jf464sbh8cisFb/W4p0Nj/JdwFhSrj848c8FY1oDvtv0TS/pn9QLNZ8lcuB7hsuTwK9cS/l4o/V/4AUAE0ADuw9qRXv0byj2X+g+0VzwnwyLxP8hBP/Bu8z5/iDwCVwRLAjqT6P7J8HsP78hMDNUvSYpeODLDTN3HZ3PG3PFW8sf+WrCzboIEc8PlHxpgAbEf3W199jKS35fwyszTYBITY+Je4fM74W57iyh8AKoYJwHa46TMteqkQm/42Xvk/XfwrfwBA5mgAtmHNiXueKPkbQ+fISeJuc0t35V+WCWhZdmujXPj8I2M0ANtg8r8PnSEnibvP4cofAKqNPQBb0X1S55slHRY6Rw42XvmH+kpfAEBRMAHYCpdfUJpxW+MSN5s7/sclG/u/hAehoMr4/CMHNABbWHXCHntJnvfO/1Yb3O3/Y8b+AIBB9GpbiOL4XRrst9vF4JX/zYz9AQAvYwKwGZ+vqOdu+9/ePuP/xKXyjv23VJoHoZRlVotS4fOPjNEAbGbNks7jI3lX6BwZSdxtzvibn+TKHwDwCiwBbCZK/bTQGTIyeOVP8QcAbAMTgI38aNW6TSeHzpGBxL2Nxv6bYwKKKuPzj4zRAGzUW3/1LEm7hs4xTImbzRn/I678AQDbRwOwUep2Qmk67G171qRT1r6t85TQQbLm7nuGztA4S0InAIAdoQF4SaS3ho6QgT0lnx06RC5K1JwlUdQdOgPaDA8CQg54qyT1nLTXHpJmhM6B9hClSU/oDACwIzQAkrw2cIRKdY2JIjNnAgCg+FgCkOSmw0NnQPuIa8ma0BnQhrhEQcZoACTJrR2/+Q9hrBv9umee1k2hY6C9sAkA2av8O+WDffWBoXOgTZiW23yloWMAwI5UfgKw6m2TO2umCaFzoE2YHgkdAW2qLEsAZRlUgAlAHEfTQ2dAW3k4dAAAaETlGwClmho6AtqI2eLQEQCgEZVfArDYpjCyQkaSxKM7Q4dAG2IPIHJQ+bfKXe3y9b8I796J339sdegQANCIyjcAJu0WOgPahNvC0BEAoFGVXwKQlf4bAFEQHvmC0BnQxspyFwBKo/ITAEmTQgdAW3hk/I1P3h06BAA0igmAbGzoBCg/k64KnQHtjhEAskUDYBoROgJKL01SpwFAvspS/8tytwJYApA0KnQAlJ3fNOH7Tz4aOgUANIMGgL8DDJdHnw8dAQCaxRJAWcZqKCSXfjb+xsfvCp0DbY4HASEHvFXAMETu/xQ6AwAMBQ0AMETudm3HjU/+InQOVEBamuv/cmWtOJYAWALA0HSPiJKPhg6Bakhj6zcvR11NzXpDZ0BjmAAAQ2H2T2MWPPV06BiohihJu0NnaJSZlyZr1dEAAM37dcfEXb4YOgSqY2Bk/EToDI2qxQOPh86AxrAEYKwBoCkrBxTPtiuWbAgdBNUxYf/HnuheNqVf0ujQWbbHpL7R1z7zVOgcaAwTAKBxLunsSQv+UJqrMbQHm69U0pLQOXbEpbutPDcsVh4NANAos8+PW/D490LHQDW5q/BfN23uhc+Il7EEwAoAGmDSNfUDHvu70DlQXW5+k5l9KnSO7bEo/n7oDGgcEwBgB9z183r3iHkbx7BAEBMWPLFE0tLQObbJtax+3R/vDx0DjWMCwAQA2/fLF73v7faTF14MHQQws6+6/Guhc2ydfyl0AjSHCQCwLW4/6EiTt+y24IWe0FEASaqvrX1TUuGeP2HSEx3e8a3QOdAcGgBga8y/1fH8Y//TFjzVHzoK8BL7yfIX3f3C0DlewezjtmDZ+tAx0JzKD8DXnj6FW1awuQGZXdJxzWOXcjsTisglW3v6lJ+adFzoLJJk8ls7rn3iraFzoHnsAaAHwib+lBSdOe6aP94ROgmwLSZ5j0Vnpe73SdojcJznI6XzAmfAELEEAEiS64caOXDIuGsp/ii++jV/fM5Mp0taFzDGOslOHXvtk88EzIBhqPzl79oz9mLMW2FmekKpfaTj2j/eEDoL0KzuM6e8w13XSdbiaa4PyHXauGt5MFaZMQFAVW0w05fX7TRqBsUfZdVx9eM3KopPMVNfq17TTH3uejvFv/yYADABqJpek/5v7PFlY6599MnQYYAsrD6za2bk0fWS9sn1hdyXp67/NeG6x+/J9XXQEjQAZ9IAVMRzLr/CfNSXx13zyJ9DhwGytnL2PuNrtfQLMs1T9uf2VPL/2GAjPrLzVcvXZvyzEQgNAA1AO+uV+fdcunrc03v/1BYtGggdCMjb2jOmHC6zf5Z0TBY/z2U/V+oXj7/2sV9l8fNQHDQANADtJDHZfe5apMgW9UW9C/f4znO9oUMBIaw5a683WqpzZDpV0rhmf7tkN3jq36Dwty8agLNoAEqkV1KPpF6TrXLzZyR/2NLo94r8kYGa7pv4zcdWhw4JFInP3WunnvV+eCodY2YzJO2nwecH1Df+kh5Jz0p6xKUHI9PC+oraXfaT5Xz/RZujAShLA2BaMO7Kx04LHQMA0B54EiA9EACggmgAqP8AgAriQUAAAFQQDQAAABXEEgBLAACACmICAABABdEAAABQQSwBlGUJoCw5AQClwAQAAIAKogEAAKCCKr8EYFaW2XpZcgIAyoAJAAAAFUQDAABABVV+CYDJOgCgipgAAABQQTQAAABUEEsAZVkCKEtOAEApMAEAAKCCaAAAAKgglgBK8yAgAACywwQAAIAKogEAAKCCWAJgBQAAUEFMAAAAqCAaAAAAKoglgLIsAZQlJ4Bh8/Onjep+MT3U0uhgSdMkf5XJx7gslavf5c9YpN+nHt03bs89f2PzFw2EzozyoQEAgALwC/Yc3dsz8h2SndHT78eabLTkL///l64CTDKZ5FIkV+9TT/R2nz31Vsmurq8Z9QNbsGx9oD8CSoYGAAACWnHWtHEjR6cX9HTb+yTt2uzvd9lYSadIfkrP+HXPrD176hc7ov5/tSue6cs+LdoJewCsJAeAttNzzrQ5I0f7wzKbL9OuGZwrJpvpc90++rdrz5l6Suv/RCgTJgBUVwAttuL8aeNGrrOvu/z0PJ5GatIUSTeuPWfad9aNGPXe3f5tWU/mL4LSYwIAAC20+uz99h65Tr+R/PS8X8ukOaM3vHhn73te+6q8XwvlQwMQerTPMgBQGd1n7/vaOBr4pUz7tvDccbBrwy9Xv2fa1Fb9OVEONAAA0AJ9573m1R75TyRr+dW4S3vH0qI17546rdWvjeKiAQCAnPncvXZK0vRHG9fmQ9kziu02JgF4CQ1A6LF+owfvFFBaPSNrn5fpkODnEVNnbFpIEwCJsgIAuVp7ztQjZHpf6Byb6YxNi9a8l+WAqqMBAICc+HxFFtlXVbxtvHtGCcsBVUcDEH4k19gBoHS6n532NpleF/z8sa3lgIjlgCqjAQCAnJjpw6Ez7ABNQIXRAJiV5OCtAsqk/317T5HZm8KfO3Z4dMax0QRUEFUFAHKwIYnPUHkW8AabgL99zT6hg6B1aAAAIAcW2bGhMzSpM5YvYhJQHTQA4TfiNHbwTgGl4fMVSTo8+Hmj+aMzrjEJqArKCgBkbN0Le3dKqofOMUSdsfmi1eczCWh3NAAAkLEBj8p+Bd0Zp3Ybk4D2RgMQfuTW2AGgNNziCcHPGcM/53TFEZOAdkYDAAAZizwdEzpDRpgEtDEaAADImEsvhs6QISYBbYoGIPxDOBo8Qv9FAWiUxVob/pyR6dEZe8wkoM3QAABAxtIofjx0hux5VxyLSUAboQEAgIx19Nf/IGlD6Bw5YBLQRmgAQu+0bfTgnQJKw65YskGmJcHPG7kc3hXXmAS0A8oKAOTATItCZ8hRZ6z4ttUXMAkoMxoAAMiBpfbd0Bny5V3xAJOAMqMBCD5Oa/AAUCpjv/rwb2R6OPi5I9+jMzYmAWVFAwAAufEvhk6QPyYBZUUDAAA5qcf935L0TOgcuWMSUEo0AOFHaCwDAG3KLn+q38w+Efzc0ZLDu+KUSUCZ0ACE/1fTxAGgbMZ+6eGr5NHPwp8/WnJ0xlF82+r377d3Zn+ByA0NAADkyCQ3q/2NpD+FztIiXXGs25kEFB8NQPCGucGDdwoorfqXlj7n8tky9Qc/l7Tm6IxjJgFFR1kBgBYY96VH7nTTGZIGQmdpkcEnBtIEFBYNAAC0yLjLH75JbqerPb8nYGu64hrLAUVFAxB+VNbYAaAtdHzpd99VZGfItCH4eaVVywG1eOHqj9EEFA0NAAC0WMcXfvddmZ2h6kwCOuMBmoCioQEAgABoAhAaDUD48RjLAEBFbWoCqrQckNAEFAUNAAAE1PGF331XqtgkgCagEGgACtASN3bwVgHtanASoDMl2xD+XNOSgyagAKgqwf8dNHjwTgFtreOyh2+Q+ZmqzHKAdcYpTUBIlBUAKIiOyx6+QfIzVZnlAJqAkGgAAKBAaALQKjQAwcdgDR4AKmNTE1Cl5QCnCWg1GgAAKKCOyx6+QV6xSQBNQEvRAABAQdEEIE80AMFHX00cACqn47KHb1BUseUAxQtXX/iafTL7S8RW0QAAQMF1fG7jLYJVmgQkEU1AzmgAAKAEqtcEqIsmIF80AGblOHingMobbALiM2U2EPyc1JqjK05ZDsgLZQUASqTjc8tukKIzJA2EztIiNAE5oQEAgJKhCUAWaACC7HIdwgEAm9nUBJgGgp+fWnN0xU4TkCUaAAAoqY7PLbtBXrFJAE1AZmgAAKDEaAIwVLXQAYJjvI5h6P34fpOTOHqDpNeYa4pLY00aEzoXqiaVpGcldQYO0ipdNcU/X3Xh/sdMvPR3j4UOU1Y0AECTui967QxLNMdNf51K+5m//P/oJ4HWcGmvEbKFNAFDRwMANKjnogOO80QXK/VjnEoPBEcTMDw0AFaSM3lJYrajvo8ftGcSD1zurlMHd83wZgBF4dJeNdntqy888JgJlz74h9B5yoRNgMB29Fx0wN8k8cBDkk4NnQXANnXFlixcfeGBbAxsAhMALuawFT5fUc/66V9w+Qf5jACl0FWzhI2BTWACAGzBZyvuefGAb0v+wdBZADTOpb1GRNHC/k9M7wqdpQxoAIAt9Ox7wOUynRU6B4DmubTXQOw/655/0G6hsxQdSwCMd7GZnk9Ov8Ddzw+dA8Cw7KsNG67z2TreFigJHaaomAAAG/V+avqh7n5p6BwAsmBH9+x7wCdDpygyGgBAg+v+aepXSBoZOguAjJg+2fOp/Q8MHaOoWAIoyxJAWXKWVM/+0/9W7oeEzgEgUzVPo8slHR86SBExAUDl+XtmjpD7x0LnAJAD03FrL55+VOgYRcQEoDSX1mXJWT69u647UzJuGwLalJk+JunO0DmKhgaAulp5Hmlu6AwAcnVSz0Uzdq9/ZulzoYMUCUsAqLSe+dP3kPTm0DkA5KrmsU4JHaJoaABQbYmOFf8OgArw40InKBqWAFgCqDSPdKQ8dAoALcBGwC1w5YNqS3VA6AgAWmKPNfOnTwodokhoAFBtJr4+FKiIWqKpoTMUCUsAZVkCKEvOsjFNCB0BQGu4jH/vm2ECgGozjQ0dAUBrpFI9dIYioQFAtbleDB0BQGvESteFzlAkLAEYs/VKM+uWNCZ0DAD5S0zdoTMUCRMAVJpLT4bOAKA1ajV7PHSGIqEBQKWZ9HDoDABaom/0wNKnQ4coEpYAWAGoNDPd7dJZoXMAyJnp13aJ0tAxioQJAKrN7LbQEQC0gGtR6AhFQwOASqtf8uCDkj8SOgeAnHn03dARioYlgLIsAZQlZxlFdrVc80PHAJAT09KOTz2wNHSMomECgMqzxL8uqT90DgD5cNfloTMUEQ0AKq8+f9mf5Ppm6BwAcvFER+pXhg5RRJVfArCSPAioHCnLy2r6B6V2uqSJobMAyI67f8zmL1sfOkcRMQEAJNUvXvqcuV8UOgeATN3accnS60OHKCoaAGCjsZcs/ZrJbgydA0AmnrdoYG7oEEVW+SUAZuvY3PokeveIWvIaSTNCZwEwZOvSyE4dd9FDz4YOUmRMAIDNTJx/3+pI0QmS/hg6C4AhSdz9rHEXPXBH6CBFRwMAbGHMJ+9/2mzgSMnuC50FQFMSmc/t+NRSlvIaQANgJTl4p1pq7MUPPbu+NuJoM/9u8Peeg4OjkSORbE794qXc8tcgygqwDZMuXLJm7MVLTzXpXEmrQucBsE2J3ObUP/nANaGDlAkNALADYy9+8ArfYPub9K+S1oXOA+AvUPyHiLsALHQAlEHH/Aeel/T+3n9+7T/LaudImuPStNC5gIpLZDan/ncU/6GgAShNB1CWnO1t7MUPPSvpHyX9Y/elB09XomPN/FBJ+0nqMqnuUj1sSqASErm/s34RxX+oaACAIeq48P5lkpaFzgH0Xzq9ayCNF5q0T+gsLZLIbW794geuDh2kzGgAuLAGUGL9l07vGvB4oVmFir/Z3PqF97Pbf5jYBAgAJbWp+Ffpyp/inxkaAAAoIYo/hoslgLIsAZQlJ4Dc9V86vWtAFRv7i+KfNRoAACiRvk/P6BxQVK0rf4p/LlgCAICS6Pv0jE6vUfyRDSYAjNYBlEDfZTM6fSBa6NLU0FlaZPBWP4p/bpgAAEDBUfyRByYAjAAAFNhg8a8tdHl1ir80j+KfPxoA6j+Aguq7bEanJ7WFbhUq/q559U/c/53QQaqAJQAAKKBNxb9KV/4U/5aiAQCAgqH4oxVYAijLEkBZcgIYlr7LZnR6WrGxv2le/aMU/1ZjAgAABbGp+Ffpyp/iHwwTAK6sARRA32UzOt0rduUvin9ITAAAILBNxb9KV/4U/+BoAAAgIIo/QmEJwFgDABBG32UzOl21hW6aWpH1yERu8+ofvZfiXwBMAAAggE3Fv1qP96X4FwgNAAC0GMUfRcASQFmmbmXJCWC7+i6b0elRbaF7hYq/2bz6BRT/oqEBAIAW6fvyQXt4TQshAAAMnklEQVQmA9Eic+0TOkuLJHKfW//wfXyxTwHRAABAC6y6/JAJ6YB+bKpQ8TebR/EvLhoARusAcubXz457n/7992U6KHSWFklkPrf+IYp/kbEJEABy1vPUI5dImhU6R4skks2rf+h+in/B0QAAQI66v3DwdDO7KHSOFhks/mz4KwWWAFgCAJAji+zfVI1zbSIx9i+TKnwod6AsHUBZcgJ4Sc/lrzte0ptD52iBwW/1+yDFv0xYAgCAvJg+EjpCCySSza1/kLF/2TABKMuFdVlyApAk9X7ldZM91VtC58hZIte76h+6hyv/EmICAAA58NRnS4pD58hRIre59Q/d++3QQTA0NAAAkI/jQwfIEVf+bYAGwEpyACgNd5nMjgp+3sjnSBRx5d8OaAAAIGP9lx88WdKE0DlykEh6V/18rvzbAQ0AAGQsiaJ2/Ka/RK559Q9w5d8uuAuA8TqAjEWxT/L2OrkMrvlzq19boQEAgIy5NCZ0hgwNPuTnfIp/u6EBaK8uHUABuOINJg8dIwuJ3N9F8W9PNABlqf9lyQlAFnl3G9T/RHKu/NsYmwABIGPuyZOhMwxTIvN31d9P8W9nNAAAkLH62ImPavCWuTIavPJ/H7v92x0NQPiHavAgIKDN2LxF62R6IPh5YygP+eHKvzJoAAAgD6bbQ0doUiLnyr9KaAAAIAee+vdCZ2hCInHlXzU0AOFHbiwDAG2o/ud775TpieDnjUbG/hFX/lVEAwAAObD5SuX2ldA5dmDwPv+/5cq/imgAACAnLya1KyRfGTrHNgwWf678K4sGwKwcR8QaAFA2O3/gV2tddknw88crj1Syd1P8q40GAAByVN9l6tckvzt0js0kMptXf++Sb4UOgrBoAAAgR3bagmQgsjMkrQmdRVIq17vr5/2GK3/QABRgB25jB4DSmnDukkfNfI5MA0F3+3Plj83QAABAC4w9754fmuw8KcjXBCWSvYsrf2yOBgAAWmTseb/5d8nfKWlDC1/2RTedQfHHlmgAQo/2WQYAKqV+3j1XeuwnyPSnFpw3Ho9MszrOXbKgdX9ClAUNAAC0WMc599ymqHaIS9/P6SVcrqsGkvWvG3Pukl/l9BoouVroAABQRfVzfvWcpFN6vvbfTpDZv0g6JIuf67K7PEo/Me6ce+7I4uehfdEAWElm62XJCaAp9fPuuUXSLT1X/Le3uuxck50oaacmf0yvpB94al/rOO/uX2SfEu2IBgAACqD+nnv+U9J/rvz6zPGjIjvaUx0ts4MknyZpD0kjN/7SFyV/VrLfy3WfyW8fM3rDInvnA73h0qOMaAAAoEAmnbtkjaSbNh6b+NdnjtCzHW7zFw2ESYZ2QwPAZB1ACdi5S1p56yAqgLsAAACoIBoAAAAqiCUAlgAAABXEBAAAgApiAlCWCUBZcgIASoEJAAAAFcQEgEtrAEAF0QBQ/wEAFcQSAAAAFUQDAABABbEEwBIAAKCCmAAAAFBBNAAAAFQQSwBlWQIoS04AQCkwAQAAoIJoAAAAqCCWAIzZOgCgepgAAABQQTQAAABUEEsArAAAACqICQAAABVEAwAAQAWxBFCWJYCy5AQAlAITAAAAKogJAAC0OZ+vqHfqGw6U+YGuaD95upu51SXJzXuk6DlT+rDS6MGxf/zVUpuvNHRm5I8GoDQPAipLTgBF4AuPrvU91fdWl/1Nr+ktknaWbPBMYtGmU4ptOrdEUiz1Tjvszz1X2q1mftWYyaNvtWMWDYT5EyBvNAAA0Eb8+sNH96z3s3ufXvdRmXUN4UfsIvmZ7jqz9+n+x7uvPOzz9Q2j/93mLVqXeVgExR4AAGgTPVceelzv+vRek39Z8qEU/y1NMemrPSP6l/VeddhJGfw8FAgTACbrAErO/9/RO/WO7P+spA/k8fNN2selH/dcddh3xvYMnGfnLunL43XQWkwAAKDEeq4/dI/ekX2LlVPx38Kc3nrtFz1XH7Z7C14LOaMBAICS6r/qiCm2we6U7HUtfNmZ5v7L/m/PzGKJAQHRAFhJDt4pAJtZe/XMXRJLbnGzqa0+H7nZ1HRE7efd3z5itxb9cZEDygoAlIwvPLoWqXajpP2DZXBNs1pynV8/Ow6VAcNDAwAAJdPzbN98SW8KnUPS0T0DT1wSOgSGhgYg9Gi/0QMAJHVf+/oZZvbx4OekjYeZLuq5+rCDcv+DI3OVvw3w5adgAUDxWRr/q5mNCJ1jMzUzu1zScaGDoDlMAACgJLqveePRZvbm0Dm25PJj+695QxGWJNCEyk8AGAAAKIsoso/KPXSMrUoVfUzSHaFzoHFMAACgBHquPmx3ub81dI7tOJEHBJULDQAAlEAURbNV7KltzSJ7R+gQaBwNQAF20TZ08E4BleaWHhf8PLTDw47N728AWaOsAEAp2JGhE+yYsxGwRGgAAKDg1l49cxdJu4bO0YDd11x/+KTQIdCYIq8ntQZ3AQAouNrIEVM9DZ2iMbXUpkpaGToHdowJAAAUXJrYhNAZGuVRUpqsVccEQOYqxRzAO/sWHD47dAoAQbzBvQSnKUmRrB46AxpDA2DaIGlk6Bg7Zm906frQKQAEUo76L5evC50Bjan8EoBJL4bOAADtIlLcEzoDGlP5BsCl9aEzAEC7SNy7Q2dAY1gCMPVK2jl0DABoBzV3JgAlUfkJgKSnQgcAgDaRjpKeDh0Cjal8A2DSY6EzAECbeNJOu6s/dAg0pvJLAG72mFTMr9cEgHKxR0InQOMqPwGQ+6OhIwBAW3CnASgRJgA13W1pSW6wBYACc9OS0BnQuMpPAMbed9cySWtC5wCAsotrtUWhM6BxlW8AbL5Smd0dOgcAlJrpidEn/+KPoWOgcZVfApAkue6Q6fjQMQCgvHxh6ARoTuUnAJLkUfq90BkAoMzM7EehM6A5NACS6m+/60Ez/S50DgAoqbWj1/uPQ4dAc1gC2MilG2W6KHQOACgd8wU8AKh8mABslKa6RjwRCACalppdHToDmkcDsFHHOxYvNem20DkAoGQeqt+zeFHoEGgeSwCbcUVfkqXHhc4BAGXhpn+x+UpD50DzeATeZtxl/T848iGX9gudBQBK4Mkxf1o31c5dsiF0EDSPJYDNmMlTt8+EzgEApWB2KcW/vJgAbMFd1vfDI38t6fWhswBAgf12zLPrDqEBKC8mAFswk0eKPho6BwAUWSo/n+JfbjQAWzH65Dtul3Rj6BwAUEQuXddx8mLumio57gLYBveB91pUO0rSbqGzAECBrIiUfiR0CAwfE4BtqP/1r56T6ZzQOQCgQFzu7x7ztrueDh0Ew0cDsB1j/8cvfyD5f4TOAQBF4KYvjj158U2hcyAbLAHswJh+f3/fWDtQrkNDZwGAcOzXY/tWXRg6BbLDBGAH7LS7+l0jTpb0ROgsABDIo55sONlOW7Y+dBBkh+cANKj7B0dOjyJbLGlc6CwA0EIvxKajdvrvdz4SOgiyRQPQhP6b3zQrTf1HMtVDZwGAFlgri44ee9Iv7g0dBNljCaAJo0+643aZHyNpZegsAJCz55TaMRT/9sUEYAh6f3LEoUqjWyRNCp0FADLntjyOkhN2Omnxo6GjID80AEO07pbDpyVp/D1JM0JnAYDMuH7tAxtOrv/1r54LHQX5YglgiHY64a7lY0bXDpe0IHQWAMiAu+vLY3pXvYniXw1MAIbJXdZ/81EXuOnTkkaHzgMAzbMVks8be9KdPwydBK1DA5CRdbe+ed+BJP2GSbNCZwGARrnZddGGgY/weN/qoQHIkLus75Yj3yPZpyXtEjoPAGzHb1OPzu846Rd8q19F0QDk4IWbjuwYMyK6QKYPSxofOg8AbOYxyT8/Ztf+b9jrl2wIHQbh0ADkaM0th0+qacSHpfRsyXYPnQdApf3W5Z8du0v/NRR+SDQALeHXTx/ZP37Sye7+HsmOE3dfAGiNNZJ9N5VdWf+v22+3+UpDB0Jx0AC0WN/NR+/p8cBJcjtJ0vGSxobOBKCtPCHXQov0o9Ej4x/ZMYvWhQ6EYqIBCMhvPnHUurj3MDe9zuUHK9UhMh0gaVTobAAKz2V6Qq7fS/aIlC6JYy3a6fg7/xA6GMqBBqCAVi08ekK8bsPuI2q2q7t2lVQLnQlAWO7eEynuTZX2xrFWjYprz3B1DwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAO/n/zQ22mk1xcx4AAAAASUVORK5CYII="
)

# Module-level UI instance
_ui_instance = None


# ---------------------------------------------------------------------------
# VersionParser
# ---------------------------------------------------------------------------
class VersionParser(object):
    """Parse version from Maya scene filename using _v## pattern."""

    VERSION_PATTERN = re.compile(r"_v(\d{2,3})(?=\.|$)")
    # Maya auto-increment suffix, e.g. ".001" in "shot_v01.001.ma"
    INCREMENT_PATTERN = re.compile(r"\.\d{3,}(?=\.\w+$)")

    @classmethod
    def _strip_increment(cls, scene_name):
        """Remove Maya's auto-increment suffix (.001) from a filename."""
        return cls.INCREMENT_PATTERN.sub("", scene_name)

    @staticmethod
    def parse(scene_name):
        """Extract version from a scene filename.

        Ignores Maya's auto-increment suffix (e.g. "shot_v01.001.ma" -> v01).

        Returns:
            tuple: (version_str, version_int) e.g. ("v01", 1)
                   or (None, None) if no version found.
        """
        clean = VersionParser._strip_increment(scene_name)
        matches = VersionParser.VERSION_PATTERN.findall(clean)
        if matches:
            digits = matches[-1]  # Use the last match
            ver_int = int(digits)
            return ("v{:02d}".format(ver_int), ver_int)
        return (None, None)

    @staticmethod
    def get_scene_base_name(scene_name):
        """Return scene name stripped of version, task name, increment suffix,
        and extension.

        The last underscore segment before the version is treated as the
        task name and removed.

        e.g. "shotNum_plateNum_taskName_v002.ma" -> "shotNum_plateNum"
             "shot_task_v01.001.ma" -> "shot"
             "shot_v01.ma" -> "shot"
        """
        clean = VersionParser._strip_increment(scene_name)
        name_no_ext = os.path.splitext(clean)[0]
        # Remove the last _v## occurrence
        parts = VersionParser.VERSION_PATTERN.findall(name_no_ext)
        if parts:
            last_ver = "_v" + parts[-1]
            idx = name_no_ext.rfind(last_ver)
            if idx >= 0:
                base = name_no_ext[:idx]
                # Drop the last underscore segment (task name)
                if "_" in base:
                    base = base.rsplit("_", 1)[0]
                return base
        return name_no_ext


# ---------------------------------------------------------------------------
# FolderManager
# ---------------------------------------------------------------------------
class FolderManager(object):
    """Create and manage export folder structure."""

    @staticmethod
    def build_export_paths(export_root, scene_base_name, version_str,
                           tag="track", qc_tag="track"):
        """Build the full set of export paths.

        Args:
            tag: Naming tag for export files (ma, fbx, abc).
                 "cam" for Camera Track, "charMM" for Matchmove,
                 "KTHead" for Face Track.
            qc_tag: Naming tag for QC playblast files (mov, png, mp4).
                    Defaults to "track" for all tabs.

        Returns:
            dict: {"ma": path, "fbx": path, "abc": path, "mov": path, ...}
        """
        paths = {}
        dir_name = "{}_track_{}".format(scene_base_name, version_str)
        dir_path = os.path.join(export_root, dir_name)
        for fmt, ext in [("ma", ".ma"), ("fbx", ".fbx"), ("abc", ".abc")]:
            file_name = "{base}_{tag}_{ver}{ext}".format(
                base=scene_base_name, tag=tag, ver=version_str, ext=ext
            )
            paths[fmt] = os.path.join(dir_path, file_name)
        # QC playblast — uses qc_tag (always "track") for consistent naming
        qc_base = "{base}_{tag}_{ver}".format(
            base=scene_base_name, tag=qc_tag, ver=version_str
        )
        paths["mov"] = os.path.join(dir_path, qc_base + ".mov")
        # PNG sequence: subfolder with same base name
        png_dir = os.path.join(dir_path, qc_base)
        paths["png_dir"] = png_dir
        paths["png_file"] = os.path.join(png_dir, qc_base)
        # MP4 (ffmpeg) output and temp directory
        paths["mp4"] = os.path.join(dir_path, qc_base + ".mp4")
        mp4_tmp_dir = os.path.join(dir_path, "_tmp_mp4")
        paths["mp4_tmp_dir"] = mp4_tmp_dir
        paths["mp4_tmp_file"] = os.path.join(mp4_tmp_dir, qc_base)
        # Composite temp dirs for multi-pass MM/FT playblasts
        composite_tmp = os.path.join(dir_path, "_tmp_composite")
        paths["composite_tmp"] = composite_tmp
        paths["composite_plate"] = os.path.join(
            composite_tmp, "plate", qc_base)
        paths["composite_color"] = os.path.join(
            composite_tmp, "color", qc_base)
        paths["composite_matte"] = os.path.join(
            composite_tmp, "matte", qc_base)
        return paths

    @staticmethod
    def ensure_directories(paths):
        """Create all necessary directories for the given paths."""
        for fmt, file_path in paths.items():
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    @staticmethod
    def build_ae_export_paths(export_root, scene_base_name, version_str, geo_names):
        """Build export paths for AE JSX + OBJ files.

        Args:
            export_root: Base export directory.
            scene_base_name: Scene name without version/extension.
            version_str: Version string e.g. "v01".
            geo_names: List of geometry child names for OBJ files.

        Returns:
            dict: {"jsx": full_path, "obj": {geo_name: full_path, ...}}
        """
        main_dir_name = "{}_track_{}".format(
            scene_base_name, version_str
        )
        ae_dir_name = "{}_track_afterEffects_{}".format(
            scene_base_name, version_str
        )
        ae_dir = os.path.join(export_root, main_dir_name, ae_dir_name)
        jsx_name = "{base}_ae_{ver}.jsx".format(
            base=scene_base_name, ver=version_str
        )
        paths = {"jsx": os.path.join(ae_dir, jsx_name), "obj": {}}
        for geo_name in geo_names:
            # Strip DAG path and Maya namespaces
            # e.g. "|grp|ns:GeoName" → "GeoName"
            short_geo = geo_name.rsplit("|", 1)[-1]
            short_geo = short_geo.rsplit(":", 1)[-1]
            obj_name = "{base}_{ver}_{geo}.obj".format(
                base=scene_base_name, ver=version_str, geo=short_geo
            )
            paths["obj"][geo_name] = os.path.join(ae_dir, obj_name)
        return paths

    @staticmethod
    def ensure_ae_directories(ae_paths):
        """Create the AE subfolder if needed."""
        ae_dir = os.path.dirname(ae_paths["jsx"])
        if not os.path.exists(ae_dir):
            os.makedirs(ae_dir)

    @staticmethod
    def resolve_versioned_dir(export_root, scene_base_name, version_str):
        """Find or create the versioned export directory.

        If an older version folder exists (e.g. _track_v01), rename it
        to the current version. Existing files inside are preserved.

        Returns:
            str: Path to the export directory.
        """
        target_name = "{}_track_{}".format(scene_base_name, version_str)
        target_dir = os.path.join(export_root, target_name)
        if os.path.isdir(target_dir):
            return target_dir

        # Search for an existing _track_v## folder to rename
        prefix = scene_base_name + "_track_v"
        try:
            for entry in sorted(os.listdir(export_root)):
                if (entry.startswith(prefix)
                        and os.path.isdir(
                            os.path.join(export_root, entry))):
                    old_dir = os.path.join(export_root, entry)
                    os.rename(old_dir, target_dir)
                    return target_dir
        except OSError:
            pass

        return target_dir

    @staticmethod
    def resolve_ae_dir(parent_dir, scene_base_name, version_str):
        """Find or create the versioned AE export subdirectory.

        If an older version AE folder exists inside *parent_dir*,
        rename it to the current version.

        Returns:
            str: Path to the AE directory.
        """
        target_name = "{}_track_afterEffects_{}".format(
            scene_base_name, version_str
        )
        target_dir = os.path.join(parent_dir, target_name)
        if os.path.isdir(target_dir):
            return target_dir

        prefix = scene_base_name + "_track_afterEffects_v"
        try:
            for entry in sorted(os.listdir(parent_dir)):
                if (entry.startswith(prefix)
                        and os.path.isdir(
                            os.path.join(parent_dir, entry))):
                    old_dir = os.path.join(parent_dir, entry)
                    os.rename(old_dir, target_dir)
                    return target_dir
        except OSError:
            pass

        return target_dir


# ---------------------------------------------------------------------------
# Exporter
# ---------------------------------------------------------------------------
class Exporter(object):
    """Handles exporting to each format."""

    def __init__(self, log_callback):
        self.log = log_callback

    def _log_error(self, tag, exception):
        """Dump a verbose, readable error report to Maya's Script Editor
        (stderr shows as red text) so the artist can copy/paste it for
        support.  The in-tool UI log is kept short."""
        tb_str = traceback.format_exc()
        divider = "=" * 60
        sys.stderr.write(
            "\n{div}\n"
            "  MULTI-EXPORT  —  {tag} FAILED\n"
            "{div}\n"
            "\n"
            "  Error : {err}\n"
            "\n"
            "  Traceback (most recent call last):\n"
            "{tb}\n"
            "{div}\n\n".format(
                div=divider, tag=tag.upper(), err=exception, tb=tb_str)
        )

    def _validate_playblast_format(self):
        """Multi-layer diagnostic for .mov playblast format availability.

        Returns:
            tuple: (pb_format, diagnostics) where pb_format is
                   "avfoundation", "qt", or None; diagnostics is a
                   list of human-readable strings.
        """
        diag = []

        # Layer 1: Query Maya for available formats
        available_formats = cmds.playblast(
            format=True, query=True
        ) or []

        pb_format = None
        if "avfoundation" in available_formats:
            pb_format = "avfoundation"
            diag.append("Movie format OK (AVFoundation).")
        elif "qt" in available_formats:
            pb_format = "qt"
            diag.append("Movie format OK (QuickTime).")
        else:
            diag.append("No .mov movie format detected by Maya.")

        # Layer 2 & 3: Windows-only registry and DLL checks
        if sys.platform == "win32":
            qt_info = self._check_quicktime_windows()
            if qt_info["registry_found"]:
                ver = qt_info.get("version_str", "unknown")
                diag.append(
                    "QuickTime version {} is installed.".format(ver))
            else:
                diag.append("QuickTime is NOT installed on this machine.")

            if qt_info["qts_found"]:
                diag.append("QuickTime core files found on disk.")
            elif qt_info["registry_found"]:
                diag.append(
                    "QuickTime core files are MISSING from disk "
                    "(incomplete install).")

        return pb_format, diag

    @staticmethod
    def _check_quicktime_windows():
        """Check Windows registry and disk for QuickTime installation.

        Returns dict with keys: registry_found, install_dir,
        version_str, qts_found, qts_path.
        """
        info = {
            "registry_found": False,
            "install_dir": None,
            "version_str": None,
            "qts_found": False,
            "qts_path": None,
        }
        try:
            import winreg
        except ImportError:
            return info

        # Try multiple registry views (32-bit redirect on 64-bit Windows)
        for access_flag in (
            winreg.KEY_READ | winreg.KEY_WOW64_32KEY,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
            winreg.KEY_READ,
        ):
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Apple Computer, Inc.\QuickTime",
                    0, access_flag,
                )
                info["registry_found"] = True
                try:
                    install_dir, _ = winreg.QueryValueEx(
                        key, "InstallDir")
                    info["install_dir"] = install_dir
                except (FileNotFoundError, OSError):
                    pass
                try:
                    version_raw, _ = winreg.QueryValueEx(
                        key, "Version")
                    major = (version_raw >> 24) & 0xFF
                    minor = (version_raw >> 20) & 0x0F
                    patch = (version_raw >> 16) & 0x0F
                    info["version_str"] = "{}.{}.{}".format(
                        major, minor, patch)
                except (FileNotFoundError, OSError):
                    pass
                winreg.CloseKey(key)
                break
            except (FileNotFoundError, OSError):
                continue

        # Check for QuickTime.qts on disk
        search_dirs = []
        if info["install_dir"]:
            search_dirs.append(info["install_dir"])
        search_dirs.extend([
            r"C:\Program Files (x86)\QuickTime",
            r"C:\Program Files\QuickTime",
        ])
        for candidate in search_dirs:
            qts = os.path.join(candidate, "QTSystem", "QuickTime.qts")
            if os.path.isfile(qts):
                info["qts_found"] = True
                info["qts_path"] = qts
                if not info["install_dir"]:
                    info["install_dir"] = candidate
                break

        return info

    @staticmethod
    def _find_ffmpeg():
        """Locate the bundled ffmpeg executable.

        The expected layout after install is::

            {scripts_dir}/ExportGenie.py
            {scripts_dir}/bin/win/ffmpeg.exe      (Windows)
            {scripts_dir}/bin/mac/ffmpeg           (macOS)

        Returns:
            str or None: Absolute path to ffmpeg if found.
        """
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        # If running from __pycache__, go up one level
        if os.path.basename(scripts_dir) == "__pycache__":
            scripts_dir = os.path.dirname(scripts_dir)
        if sys.platform == "win32":
            ffmpeg_path = os.path.join(
                scripts_dir, "bin", "win", "ffmpeg.exe")
        elif sys.platform == "darwin":
            ffmpeg_path = os.path.join(
                scripts_dir, "bin", "mac", "ffmpeg")
        else:
            return None
        if os.path.isfile(ffmpeg_path):
            return ffmpeg_path
        return None

    def _encode_mp4(self, png_dir, png_base, start_frame, output_mp4):
        """Encode a PNG image sequence to H.264 .mp4 via bundled ffmpeg.

        Args:
            png_dir: Directory containing the PNG sequence.
            png_base: Base filename without frame number or extension.
            start_frame: First frame number in the sequence.
            output_mp4: Full path to the output .mp4 file.

        Returns:
            bool: True if encoding succeeded.
        """
        ffmpeg_path = self._find_ffmpeg()
        if not ffmpeg_path:
            self.log(
                "ffmpeg not found. See Script Editor.")
            return False

        fps = self._get_fps()
        seq_pattern = os.path.join(
            png_dir, "{}.%04d.png".format(png_base))

        cmd = [
            ffmpeg_path,
            "-y",
            "-framerate", str(fps),
            "-start_number", str(int(start_frame)),
            "-i", seq_pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-profile:v", "high",
            "-level", "4.2",
            "-preset", "ultrafast",
            "-crf", "18",
            "-movflags", "+faststart",
            output_mp4,
        ]

        self.log("Encoding MP4...")
        sys.stderr.write("ffmpeg cmd: {}\n".format(" ".join(cmd)))
        try:
            result = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=600,
                creationflags=getattr(
                    subprocess, "CREATE_NO_WINDOW", 0),
            )
            if result.returncode != 0:
                sys.stderr.write(
                    "ffmpeg failed (exit {}):\n{}\n".format(
                        result.returncode, result.stderr))
                self.log(
                    "MP4 encoding failed. See Script Editor.")
                return False
            self.log("MP4 encoding complete.")
            return True
        except subprocess.TimeoutExpired:
            self.log("MP4 encoding timed out. See Script Editor.")
            return False
        except Exception as e:
            sys.stderr.write("ffmpeg exception: {}\n".format(e))
            self.log("MP4 encoding error. See Script Editor.")
            return False

    def _encode_composite(self, plate_dir, plate_base,
                          color_dir, color_base,
                          matte_dir, matte_base,
                          start_frame, output_path,
                          opacity=1.0, png_output=False):
        """Composite 3 passes (plate, color, matte) via ffmpeg.

        Uses the matte as an alpha channel on the solid-color pass,
        then overlays it on the plate.

        Args:
            plate_dir: Directory of plate PNG sequence.
            plate_base: Base filename for plate sequence.
            color_dir: Directory of solid-color PNG sequence.
            color_base: Base filename for color sequence.
            matte_dir: Directory of B&W matte PNG sequence.
            matte_base: Base filename for matte sequence.
            start_frame: First frame number.
            output_path: Output file path (.mp4, .mov, or directory
                for PNG sequence when png_output=True).
            opacity: Blend opacity 0.0–1.0 for the mesh overlay.
            png_output: If True, output a PNG sequence instead of video.

        Returns:
            bool: True if encoding succeeded.
        """
        ffmpeg_path = self._find_ffmpeg()
        if not ffmpeg_path:
            self.log("ffmpeg not found — cannot composite.")
            return False

        fps = self._get_fps()
        plate_pattern = os.path.join(
            plate_dir, "{}.%04d.png".format(plate_base))
        color_pattern = os.path.join(
            color_dir, "{}.%04d.png".format(color_base))
        matte_pattern = os.path.join(
            matte_dir, "{}.%04d.png".format(matte_base))

        start_num = str(int(start_frame))

        # Build filter: matte -> alpha on color -> overlay on plate
        opacity_val = max(0.0, min(1.0, opacity))
        filter_complex = (
            "[2:v]format=gray[matte];"
            "[1:v][matte]alphamerge,format=rgba,"
            "colorchannelmixer=aa={opacity:.4f}[fg];"
            "[0:v][fg]overlay=format=auto[out]"
        ).format(opacity=opacity_val)

        cmd = [
            ffmpeg_path, "-y",
            "-framerate", str(fps),
            "-start_number", start_num,
            "-i", plate_pattern,
            "-framerate", str(fps),
            "-start_number", start_num,
            "-i", color_pattern,
            "-framerate", str(fps),
            "-start_number", start_num,
            "-i", matte_pattern,
            "-filter_complex", filter_complex,
            "-map", "[out]",
        ]

        if png_output:
            # Output as PNG sequence
            out_pattern = os.path.join(
                output_path,
                os.path.basename(output_path) + ".%04d.png")
            cmd.extend([
                "-start_number", start_num,
                out_pattern,
            ])
        else:
            cmd.extend([
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "18",
                "-preset", "ultrafast",
                "-movflags", "+faststart",
                output_path,
            ])

        self.log("Compositing passes...")
        sys.stderr.write("ffmpeg composite cmd: {}\n".format(
            " ".join(cmd)))
        try:
            result = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=600,
                creationflags=getattr(
                    subprocess, "CREATE_NO_WINDOW", 0),
            )
            if result.returncode != 0:
                sys.stderr.write(
                    "ffmpeg composite failed (exit {}):\n{}\n".format(
                        result.returncode, result.stderr))
                self.log(
                    "Composite encoding failed. See Script Editor.")
                return False
            self.log("Composite encoding complete.")
            return True
        except subprocess.TimeoutExpired:
            self.log("Composite encoding timed out.")
            return False
        except Exception as e:
            sys.stderr.write(
                "ffmpeg composite exception: {}\n".format(e))
            self.log("Composite encoding error. See Script Editor.")
            return False

    @staticmethod
    def _cleanup_temp_pngs(png_dir):
        """Delete a temporary PNG sequence directory."""
        if os.path.isdir(png_dir):
            try:
                shutil.rmtree(png_dir)
            except Exception:
                pass

    @staticmethod
    def _is_descendant_of(node, ancestor):
        """Return True if *node* is the same as or a descendant of *ancestor*."""
        if not node or not ancestor:
            return False
        node_long = cmds.ls(node, long=True)
        ancestor_long = cmds.ls(ancestor, long=True)
        if not node_long or not ancestor_long:
            return False
        # A node's long name starts with the ancestor's long name + "|"
        return (node_long[0] == ancestor_long[0]
                or node_long[0].startswith(ancestor_long[0] + "|"))

    def export_ma(self, file_path, camera, geo_roots, rig_roots, proxy_geos,
                  start_frame=None, end_frame=None):
        """Export selection as Maya ASCII.

        Camera should already be renamed to 'cam_main' by the caller.

        Args:
            geo_roots: list of geo root transforms (or empty list).
            rig_roots: list of rig root transforms (or empty list).
            proxy_geos: list of static/proxy geo transforms (or empty list).
            start_frame: If provided, the exported .ma file's playback
                range is set to this start frame (then restored).
            end_frame: If provided, the exported .ma file's playback
                range is set to this end frame (then restored).
        """
        try:
            geo_roots = geo_roots or []
            rig_roots = rig_roots or []
            proxy_geos = proxy_geos or []
            # Skip camera from selection if it's already a descendant
            # of any assigned group — it will be exported as part of
            # that hierarchy.
            all_roots = geo_roots + rig_roots + proxy_geos
            cam_under_root = any(
                self._is_descendant_of(camera, gr)
                for gr in all_roots if gr
            )
            effective_cam = None if cam_under_root else camera
            sel = [effective_cam] if effective_cam else []
            sel.extend(proxy_geos)
            sel.extend(geo_roots)
            sel.extend(rig_roots)
            # Include image plane transforms so the source footage
            # reference is preserved in the exported .ma file.
            if camera:
                sel.extend(self._get_image_plane_transforms(camera))
            if not sel:
                self.log("MA skipped — nothing to export.")
                return False

            # Temporarily set the scene's playback range so the
            # exported .ma stores the correct frame range.
            orig_min = orig_max = orig_ast = orig_aet = None
            if start_frame is not None and end_frame is not None:
                orig_min = cmds.playbackOptions(
                    query=True, minTime=True)
                orig_max = cmds.playbackOptions(
                    query=True, maxTime=True)
                orig_ast = cmds.playbackOptions(
                    query=True, animationStartTime=True)
                orig_aet = cmds.playbackOptions(
                    query=True, animationEndTime=True)
                cmds.playbackOptions(
                    minTime=start_frame, maxTime=end_frame,
                    animationStartTime=start_frame,
                    animationEndTime=end_frame)

            # Replace all custom shaders with the default lambert so
            # the exported .ma contains only default materials.
            original_shading = {}
            all_meshes = []
            for node in sel:
                if node and cmds.objExists(node):
                    descendants = cmds.listRelatives(
                        node, allDescendents=True,
                        type="mesh", fullPath=True) or []
                    all_meshes.extend(descendants)
            for mesh in all_meshes:
                try:
                    sgs = cmds.listConnections(
                        mesh, type="shadingEngine") or []
                    if sgs and sgs[0] != "initialShadingGroup":
                        original_shading[mesh] = sgs[0]
                        cmds.sets(mesh, edit=True,
                                  forceElement="initialShadingGroup")
                except Exception:
                    pass

            # Create metadata group with version and export date
            info_grp = cmds.group(em=True, name="ExportGenie_info")
            cmds.addAttr(info_grp, ln="notes", dt="string")
            cmds.setAttr(
                info_grp + ".notes",
                "Export Genie {} | {}".format(
                    TOOL_VERSION,
                    datetime.date.today().isoformat()),
                type="string")
            sel.append(info_grp)

            try:
                cmds.select(sel, replace=True)
                cmds.file(
                    file_path,
                    exportSelected=True,
                    type="mayaAscii",
                    force=True,
                    preserveReferences=False,
                    channels=True,
                    expressions=True,
                    constraints=True,
                    constructionHistory=True,
                )
            finally:
                # Remove temporary metadata group from scene
                if cmds.objExists(info_grp):
                    try:
                        cmds.delete(info_grp)
                    except Exception:
                        pass
                # Restore original shading assignments
                for mesh, sg in original_shading.items():
                    try:
                        if cmds.objExists(mesh) and cmds.objExists(sg):
                            cmds.sets(mesh, edit=True,
                                      forceElement=sg)
                    except Exception:
                        pass
                # Restore original playback range
                if orig_min is not None:
                    cmds.playbackOptions(
                        minTime=orig_min, maxTime=orig_max,
                        animationStartTime=orig_ast,
                        animationEndTime=orig_aet)
            return True
        except Exception as e:
            self._log_error("MA", e)
            return False

    @staticmethod
    def _create_metadata_grp():
        """Create a temporary empty group whose name encodes version + date."""
        name = "ExportGenie_{}_{}".format(
            TOOL_VERSION,
            datetime.date.today().isoformat().replace("-", ""))
        grp = cmds.group(em=True, name=name)
        return grp

    def export_fbx(self, file_path, camera, geo_roots, rig_roots, proxy_geos,
                   start_frame, end_frame,
                   export_input_connections=False):
        """Export camera + geo + rig + proxy geo as FBX with baked keyframes.

        UE5-conforming settings: Resample All ON, Tangents ON, Up Axis Y.

        Args:
            geo_roots: list of geo root transforms (or empty list).
            rig_roots: list of rig root transforms (or empty list).
            proxy_geos: list of static/proxy geo transforms (or empty list).
            export_input_connections: If True, the FBX plugin follows
                input connections (deformers, anim curves) from the
                selected nodes.  Required for blendshape weight
                animation export; the plugin must discover the
                blendShape node via the mesh's deformation chain.
        """
        try:
            geo_roots = geo_roots or []
            rig_roots = rig_roots or []
            proxy_geos = proxy_geos or []
            # Ensure FBX plugin is loaded
            if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
                try:
                    cmds.loadPlugin("fbxmaya")
                except Exception:
                    self.log("FBX plugin not available. See Script Editor.")
                    cmds.confirmDialog(
                        title="FBX Plugin Not Found",
                        message=(
                            "Export Genie {}\n\n"
                            "The FBX plugin (fbxmaya) could not be loaded.\n\n"
                            "To enable it, go to:\n"
                            "Windows > Settings/Preferences > Plug-in Manager\n\n"
                            "Find 'fbxmaya' in the list and check 'Loaded'."
                        ).format(TOOL_VERSION),
                        button=["OK"],
                    )
                    return False

            # Skip camera from selection if it's already a descendant
            # of any assigned group.
            all_roots = geo_roots + rig_roots + proxy_geos
            cam_under_root = any(
                self._is_descendant_of(camera, gr)
                for gr in all_roots if gr
            )
            effective_cam = None if cam_under_root else camera
            sel = [effective_cam] if effective_cam else []
            sel.extend(proxy_geos)
            sel.extend(geo_roots)
            sel.extend(rig_roots)

            # Auto-include deformation skeleton roots that are skin
            # influences on the exported geo but live outside
            # rig_roots (e.g. a separate Joint_GRP group).
            sel_long = set()
            for s in sel:
                if s:
                    sel_long.update(cmds.ls(s, long=True) or [])
            for geo_root in geo_roots:
                if not geo_root or not cmds.objExists(geo_root):
                    continue
                descendants = cmds.listRelatives(
                    geo_root, allDescendents=True, type="transform",
                    fullPath=True
                ) or []
                geo_long = (cmds.ls(geo_root, long=True)
                            or [geo_root])
                for desc in geo_long + descendants:
                    shapes = cmds.listRelatives(
                        desc, shapes=True, type="mesh",
                        fullPath=True
                    ) or []
                    if not shapes:
                        continue
                    history = cmds.listHistory(
                        desc, pruneDagObjects=True) or []
                    for h in history:
                        if cmds.objectType(h) != "skinCluster":
                            continue
                        influences = cmds.skinCluster(
                            h, query=True, influence=True
                        ) or []
                        # Resolve to long paths
                        influences = [
                            p for i in influences
                            for p in (cmds.ls(i, long=True) or [i])]
                        for inf in influences:
                            # Walk up to the topmost joint
                            current = inf
                            while True:
                                parent = cmds.listRelatives(
                                    current, parent=True,
                                    fullPath=True
                                )
                                if (not parent
                                        or cmds.objectType(
                                            parent[0]) != "joint"):
                                    break
                                current = parent[0]
                            # Check if already covered by selection
                            long_inf = (cmds.ls(current, long=True)
                                        or [current])[0]
                            covered = any(
                                long_inf.startswith(s + "|")
                                or long_inf == s
                                for s in sel_long)
                            if not covered and current not in sel:
                                # Include the parent group so the
                                # full joint hierarchy is exported
                                parent = cmds.listRelatives(
                                    current, parent=True,
                                    fullPath=True
                                )
                                include = parent[0] if parent else current
                                if include not in sel:
                                    sel.append(include)
                                    sel_long.update(
                                        cmds.ls(include,
                                                long=True) or [])
                                    sys.stderr.write(
                                        "[ExportGenie]   Auto-added "
                                        "skin influence root to FBX "
                                        "selection: '{}'\n".format(
                                            include))

            if not sel:
                self.log("FBX skipped — nothing to export.")
                return False

            sys.stderr.write(
                "[ExportGenie] FBX export selection: {}\n".format(sel))
            sys.stderr.write(
                "[ExportGenie]   geo_roots: {}\n".format(geo_roots))
            sys.stderr.write(
                "[ExportGenie]   rig_roots: {}\n".format(rig_roots))
            sys.stderr.write(
                "[ExportGenie]   proxy_geos: {}\n".format(proxy_geos))
            sys.stderr.write(
                "[ExportGenie]   camera: {} (under root: {})\n".format(
                    camera, cam_under_root))
            sys.stderr.write(
                "[ExportGenie]   frame range: {} - {}\n".format(
                    start_frame, end_frame))
            sys.stderr.write(
                "[ExportGenie]   export_input_connections: "
                "{}\n".format(export_input_connections))

            # Log skinCluster -> dagPose state at export time
            sc_at_export = cmds.ls(type="skinCluster") or []
            dp_at_export = cmds.ls(type="dagPose") or []
            sys.stderr.write(
                "[ExportGenie]   skinClusters at export: {}\n".format(
                    sc_at_export))
            sys.stderr.write(
                "[ExportGenie]   dagPose nodes at export: {}\n".format(
                    dp_at_export))
            for sc in sc_at_export:
                infs = cmds.skinCluster(
                    sc, query=True, influence=True) or []
                geo = cmds.skinCluster(
                    sc, query=True, geometry=True) or []
                sys.stderr.write(
                    "[ExportGenie]     '{}': {} influences, "
                    "geo={}\n".format(sc, len(infs), geo))
            for dp in dp_at_export:
                members = cmds.dagPose(
                    dp, query=True, members=True) or []
                sys.stderr.write(
                    "[ExportGenie]     dagPose '{}': {} "
                    "members\n".format(dp, len(members)))

            # Set FBX export options
            mel.eval("FBXResetExport")
            # Include Options
            mel.eval("FBXExportInputConnections -v {}".format(
                "true" if export_input_connections else "false"))
            mel.eval("FBXExportEmbeddedTextures -v false")
            # Animation
            mel.eval("FBXExportQuaternion -v resample")
            # Bake Animation — FBX plugin bakes internally without
            # modifying the source scene
            mel.eval("FBXExportBakeComplexAnimation -v true")
            mel.eval(
                "FBXExportBakeComplexStart -v {}".format(int(start_frame))
            )
            mel.eval(
                "FBXExportBakeComplexEnd -v {}".format(int(end_frame))
            )
            mel.eval("FBXExportBakeComplexStep -v 1")
            mel.eval("FBXExportBakeResampleAnimation -v true")
            # Deformed Models
            mel.eval("FBXExportSkins -v true")
            mel.eval("FBXExportShapes -v true")
            # General
            mel.eval("FBXExportSmoothingGroups -v true")
            mel.eval("FBXExportTangents -v true")
            mel.eval("FBXExportSmoothMesh -v false")
            mel.eval("FBXExportConstraints -v false")
            mel.eval("FBXExportCameras -v true")
            mel.eval("FBXExportLights -v false")
            mel.eval("FBXExportSkeletonDefinitions -v true")
            mel.eval("FBXExportInAscii -v false")
            mel.eval('FBXExportFileVersion -v "FBX202000"')
            mel.eval("FBXExportUpAxis z")
            mel.eval("FBXExportConvertUnitString cm")
            mel.eval("FBXExportScaleFactor 1")
            mel.eval("FBXExportUseSceneName -v false")

            # Create metadata group and include in export
            info_grp = self._create_metadata_grp()
            sel.append(info_grp)

            try:
                cmds.select(sel, replace=True)
                mel_path = file_path.replace("\\", "/")
                mel.eval('FBXExport -f "{}" -s'.format(mel_path))
            finally:
                if cmds.objExists(info_grp):
                    try:
                        cmds.delete(info_grp)
                    except Exception:
                        pass

            return True
        except Exception as e:
            self._log_error("FBX", e)
            return False

    def export_abc(self, file_path, camera, geo_roots, proxy_geos,
                   start_frame, end_frame):
        """Export camera + geo roots + proxy geo as Alembic cache.

        Args:
            geo_roots: list of geo root transforms (or empty list).
            proxy_geos: list of static/proxy geo transforms (or empty list).
        """
        try:
            geo_roots = geo_roots or []
            proxy_geos = proxy_geos or []
            # Ensure Alembic plugin is loaded
            if not cmds.pluginInfo("AbcExport", query=True, loaded=True):
                try:
                    cmds.loadPlugin("AbcExport")
                except Exception:
                    self.log("ABC plugin not available. See Script Editor.")
                    cmds.confirmDialog(
                        title="Alembic Plugin Not Found",
                        message=(
                            "Export Genie {}\n\n"
                            "The Alembic plugin (AbcExport) could not be loaded.\n\n"
                            "To enable it, go to:\n"
                            "Windows > Settings/Preferences > Plug-in Manager\n\n"
                            "Find 'AbcExport' in the list and check 'Loaded'."
                        ).format(TOOL_VERSION),
                        button=["OK"],
                    )
                    return False

            if not camera and not geo_roots and not proxy_geos:
                self.log("ABC skipped — nothing to export.")
                return False

            # Build root flags — skip camera if it's already under
            # any assigned group.
            all_roots = geo_roots + proxy_geos
            cam_under_root = any(
                self._is_descendant_of(camera, gr)
                for gr in all_roots if gr
            )
            # Create metadata group and include as a root
            info_grp = self._create_metadata_grp()

            root_flags = ""
            root_nodes = [camera] + geo_roots + proxy_geos + [info_grp]
            for node in root_nodes:
                if not node:
                    continue
                if node == camera and cam_under_root:
                    continue
                long_names = cmds.ls(node, long=True)
                if not long_names:
                    if node == info_grp:
                        continue
                    self.log(
                        "ABC failed — '{}' not found.".format(node)
                    )
                    return False
                root_flags += "-root {} ".format(long_names[0])

            abc_path = file_path.replace("\\", "/")

            job_string = (
                "-frameRange {start} {end} "
                "-uvWrite "
                "-worldSpace "
                "-wholeFrameGeo "
                "-dataFormat ogawa "
                "{roots}"
                "-file '{file}'"
            ).format(
                start=int(start_frame),
                end=int(end_frame),
                roots=root_flags,
                file=abc_path,
            )

            try:
                cmds.AbcExport(j=job_string)
            finally:
                if cmds.objExists(info_grp):
                    try:
                        cmds.delete(info_grp)
                    except Exception:
                        pass
            return True
        except Exception as e:
            self._log_error("ABC", e)
            return False

    # --- OBJ Export ---

    def export_obj(self, file_path, geo_node):
        """Export a single Maya object as OBJ in local space.

        Maya's OBJ exporter writes vertices in world space.  To avoid a
        double-offset in After Effects (where the JSX also sets position/
        rotation/scale), we temporarily reset the node's world matrix to
        identity so vertices are written in local (object) space.

        Args:
            file_path: Output .obj path.
            geo_node: Maya transform node to export.

        Returns:
            bool: True on success.
        """
        try:
            if not cmds.pluginInfo("objExport", query=True, loaded=True):
                cmds.loadPlugin("objExport")

            # Save the current world matrix and reset to identity so the
            # OBJ exporter writes vertices in local space.
            orig_m = cmds.xform(geo_node, query=True,
                                worldSpace=True, matrix=True)
            identity = [1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1]
            cmds.xform(geo_node, worldSpace=True, matrix=identity)

            try:
                cmds.select(geo_node, replace=True)
                cmds.file(
                    file_path,
                    exportSelected=True,
                    type="OBJexport",
                    force=True,
                    options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1",
                )
            finally:
                # Always restore the original transform.
                cmds.xform(geo_node, worldSpace=True, matrix=orig_m)

            return True
        except Exception as e:
            self._log_error("OBJ", e)
            return False

    @staticmethod
    def _is_simple_plane(node):
        """Return True if *node* is a flat/planar mesh (suitable for AE solid).

        Checks whether the world-space bounding box is effectively flat
        along one axis (thinnest extent < 0.1 % of the largest).  This
        catches simple quads as well as subdivided planes.
        """
        shapes = cmds.listRelatives(node, shapes=True, type="mesh") or []
        if not shapes:
            return False
        try:
            bbox = cmds.exactWorldBoundingBox(node)
            extents = [bbox[3] - bbox[0],
                       bbox[4] - bbox[1],
                       bbox[5] - bbox[2]]
            max_ext = max(extents)
            if max_ext < 1e-9:
                return False
            min_ext = min(extents)
            return min_ext / max_ext < 0.001
        except Exception:
            return False

    # --- Face Track: BlendShape conversion helpers ---

    @staticmethod
    def _unique_name(base):
        """Return a unique Maya node name based on *base*."""
        if not cmds.objExists(base):
            return base
        i = 1
        while cmds.objExists("{}{}".format(base, i)):
            i += 1
        return "{}{}".format(base, i)

    @staticmethod
    def _copy_rotate_order_and_pivots(src, tgt):
        """Copy rotate order and world-space pivots from *src* to *tgt*."""
        try:
            ro = cmds.getAttr(src + ".rotateOrder")
            cmds.setAttr(tgt + ".rotateOrder", ro)
        except Exception:
            pass
        try:
            rp = cmds.xform(src, q=True, ws=True, rp=True)
            sp = cmds.xform(src, q=True, ws=True, sp=True)
            cmds.xform(tgt, ws=True, rp=rp)
            cmds.xform(tgt, ws=True, sp=sp)
        except Exception:
            pass

    @staticmethod
    def _bake_local_trs(src, tgt, start, end):
        """Bake TRS onto *tgt* to match *src* via constraints, then remove them."""
        for a in ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"):
            try:
                cmds.setAttr("{}.{}".format(tgt, a),
                             lock=False, keyable=True, channelBox=True)
            except Exception:
                pass

        pc = cmds.parentConstraint(src, tgt, mo=True)[0]
        sc = None
        try:
            sc = cmds.scaleConstraint(src, tgt, mo=True)[0]
        except Exception:
            sc = None

        cmds.bakeResults(
            tgt,
            t=(start, end),
            at=["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"],
            simulation=True,
            preserveOutsideKeys=True,
            minimizeRotation=True,
        )

        cmds.delete(pc)
        if sc:
            cmds.delete(sc)

    def convert_abc_to_blendshape(self, src_xform, start_frame, end_frame,
                                   targets_group_name="BS_Targets_GRP",
                                   blendshape_suffix="_BS",
                                   base_suffix="_BSBase"):
        """Convert Alembic per-vertex animation to FBX-ready blendShapes.

        Two-pass approach: creates all targets first, then keys all
        weights.  After keying, target shapes, the targets group, and
        the original source mesh are deleted — the blendShape node
        stores deltas internally, so only the base mesh is needed for
        FBX export.  Caller should wrap in an undo chunk to restore
        the scene afterward.

        Returns:
            dict with keys: base_mesh, blendshape_node
        """
        start = int(start_frame)
        end = int(end_frame)
        frames = list(range(start, end + 1))

        original_time = cmds.currentTime(q=True)
        # Strip namespace and DAG path for clean naming
        short_name = src_xform.split("|")[-1].rsplit(":", 1)[-1]

        self.log("Creating blendshapes for '{}' — {} frames...".format(
            short_name, len(frames)))

        # Preserve hierarchy: parent base under same parent as source
        src_parent = (cmds.listRelatives(
            src_xform, parent=True, fullPath=True) or [None])[0]

        # Create base mesh at start frame
        cmds.currentTime(start, e=True)
        base_name = self._unique_name(short_name + base_suffix)
        base_mesh = cmds.duplicate(src_xform, rr=True, name=base_name)[0]
        cmds.delete(base_mesh, ch=True)

        # Re-parent only if the duplicate ended up under a different parent
        if src_parent:
            base_parent = (cmds.listRelatives(
                base_mesh, parent=True, fullPath=True) or [None])[0]
            if base_parent != src_parent:
                try:
                    cmds.parent(base_mesh, src_parent)
                except Exception as exc:
                    sys.stderr.write(
                        "[ExportGenie] Could not parent base "
                        "under {}: {}\n".format(
                            src_parent, exc))

        self._copy_rotate_order_and_pivots(src_xform, base_mesh)
        self._bake_local_trs(src_xform, base_mesh, start, end)

        # Create blendShape node on the base mesh
        bs_name = self._unique_name(short_name + blendshape_suffix)
        bs_node = cmds.blendShape(
            base_mesh, name=bs_name, origin="local")[0]

        # Targets group (hidden)
        grp_name = self._unique_name(targets_group_name)
        grp = cmds.group(em=True, name=grp_name)
        try:
            cmds.setAttr(grp + ".visibility", 0)
        except Exception:
            pass

        # --- Pass 1: create all targets and add to blendShape ---
        for i, f in enumerate(frames):
            cmds.currentTime(f, e=True)

            tgt_name = self._unique_name(
                "{}_f{:04d}".format(short_name, f))
            tgt = cmds.duplicate(src_xform, rr=True, name=tgt_name)[0]
            cmds.delete(tgt, ch=True)

            try:
                cmds.parent(tgt, grp)
            except Exception:
                pass

            cmds.blendShape(
                bs_node, e=True, t=(base_mesh, i, tgt, 1.0))

            if (i + 1) % 50 == 0 or (i + 1) == len(frames):
                self.log("  {}/{} targets created...".format(
                    i + 1, len(frames)))

        # --- Pass 2: key all weights by index ---
        # Use weight[i] indexing (guaranteed creation order) instead of
        # alias names (which may be reordered or mangled by _unique_name
        # collisions).
        for i, f in enumerate(frames):
            w = "{}.weight[{}]".format(bs_node, i)

            try:
                cmds.cutKey(w, clear=True)
            except Exception:
                pass

            if f > start:
                cmds.setKeyframe(w, t=f - 1, v=0.0)
            cmds.setKeyframe(w, t=f, v=1.0)
            cmds.setKeyframe(w, t=f + 1, v=0.0)

            # Step tangents for hold
            try:
                cmds.keyTangent(
                    w, time=(f, f), itt="stepnext", ott="step")
                cmds.keyTangent(
                    w, time=(f + 1, f + 1), itt="stepnext", ott="step")
            except Exception:
                pass

        # Diagnostic: verify keyframes were set
        keyed_count = 0
        for i in range(len(frames)):
            w = "{}.weight[{}]".format(bs_node, i)
            kc = cmds.keyframe(w, query=True, keyframeCount=True) or 0
            if kc > 0:
                keyed_count += 1
        self.log("Keyed {}/{} blendshape weights on '{}'.".format(
            keyed_count, len(frames), bs_node))

        # Delete target shapes and their group — the blendShape node
        # stores deltas internally, so the physical targets are no
        # longer needed.  Keeping them causes FBX InputConnections to
        # pull them into the export as extra geometry (visible in
        # other DCCs even though hidden in Maya).
        if cmds.objExists(grp):
            try:
                cmds.delete(grp)
            except Exception as exc:
                sys.stderr.write(
                    "[ExportGenie] WARNING: Could not delete targets "
                    "group '{}': {}\n".format(grp, exc))

        # Delete original Alembic source mesh — prevents the FBX
        # exporter from including the original (still Alembic-driven)
        # mesh via InputConnections (visual glitching / double geo).
        if cmds.objExists(src_xform):
            try:
                cmds.delete(src_xform)
            except Exception as exc:
                sys.stderr.write(
                    "[ExportGenie] WARNING: Could not delete source "
                    "mesh '{}': {}\n".format(src_xform, exc))

        self.log("Prepared {} target(s) for FBX export.".format(
            len(frames)))

        # Restore original time
        cmds.currentTime(original_time, e=True)

        self.log("Blendshape conversion complete.")
        return {
            "base_mesh": base_mesh,
            "blendshape_node": bs_node,
            "targets_group": grp,
        }

    # --- Face Track: classification helpers ---

    @staticmethod
    def _has_driven_transforms(transform):
        """Return True if any TRS channel has an incoming connection.

        Catches AlembicNode, animCurve, expression, constraint, or any
        other driver on translate/rotate/scale channels.
        """
        for attr in ("translateX", "translateY", "translateZ",
                     "rotateX", "rotateY", "rotateZ",
                     "scaleX", "scaleY", "scaleZ"):
            try:
                conns = cmds.listConnections(
                    "{}.{}".format(transform, attr),
                    source=True, destination=False
                ) or []
                if conns:
                    return True
            except Exception:
                pass
        return False

    @staticmethod
    def _bake_transform_curves(transform, start, end):
        """Bake TRS channels in-place on *transform* via cmds.bakeResults.

        Replaces driving connections (expressions, constraints, anim layers)
        with simple keyframe curves. Only bakes the individual transform,
        not its parent or children.  After baking, any non-animCurve upstream
        connections (e.g. AlembicNode) are explicitly disconnected so the FBX
        exporter won't discover and re-export them.
        """
        trs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        for a in trs:
            try:
                cmds.setAttr("{}.{}".format(transform, a),
                             lock=False, keyable=True, channelBox=True)
            except Exception:
                pass
        cmds.bakeResults(
            transform,
            t=(int(start), int(end)),
            at=trs,
            simulation=True,
            preserveOutsideKeys=True,
            minimizeRotation=True,
        )
        # Disconnect any non-animCurve sources that survived the bake
        # (e.g. AlembicNode connections). Keeps animCurve connections
        # intact since those ARE the baked result.
        for a in trs:
            plug = "{}.{}".format(transform, a)
            conns = cmds.listConnections(
                plug, source=True, destination=False,
                plugs=True, skipConversionNodes=True
            ) or []
            for src_plug in conns:
                src_node = src_plug.split(".")[0]
                if cmds.nodeType(src_node).startswith("animCurve"):
                    continue
                try:
                    cmds.disconnectAttr(src_plug, plug)
                except Exception:
                    pass

    def prep_for_ue5_fbx_export(self, geo_roots, rig_roots,
                                start_frame, end_frame, camera=None,
                                skip_mesh_xforms=None):
        """Prepare a Matchmove scene for UE5-friendly FBX export.

        Performs: bake camera, bake animation to joints, remove
        constraints, check joint scales, delete non-deformer history,
        freeze transforms on non-skinned geo, strip namespaces.

        All changes are destructive — caller MUST wrap in an undo chunk.

        Args:
            skip_mesh_xforms: optional set of long DAG paths to exclude
                from history deletion (Step 4) and freeze transforms
                (Step 5).  Used for vertex-animated meshes that will be
                converted to blendshapes after prep completes.
        """
        skip_mesh_xforms = skip_mesh_xforms or set()
        trs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

        sys.stderr.write(
            "[ExportGenie] === prep_for_ue5_fbx_export ===\n")
        sys.stderr.write(
            "[ExportGenie]   geo_roots: {}\n".format(geo_roots))
        sys.stderr.write(
            "[ExportGenie]   rig_roots: {}\n".format(rig_roots))
        sys.stderr.write(
            "[ExportGenie]   frame range: {} - {}\n".format(
                start_frame, end_frame))
        sys.stderr.write(
            "[ExportGenie]   camera: {}\n".format(camera))
        sys.stderr.write(
            "[ExportGenie]   skip_mesh_xforms: {}\n".format(
                skip_mesh_xforms))

        # --- Import references so nodes become editable ---
        # Referenced nodes are read-only; importing converts them to
        # local nodes.  Safe because caller wraps in an undo chunk.
        all_refs = cmds.ls(type="reference") or []
        refs_imported = 0
        for ref_node in all_refs:
            if ref_node == "sharedReferenceNode":
                continue
            try:
                cmds.file(referenceNode=ref_node, importReference=True)
                refs_imported += 1
            except Exception:
                pass
        if refs_imported:
            self.log("Importing references...")

        # --- Step 0: Bake camera animation ---
        if camera and cmds.objExists(camera):
            for a in trs:
                try:
                    cmds.setAttr("{}.{}".format(camera, a),
                                 lock=False, keyable=True,
                                 channelBox=True)
                except Exception:
                    pass
            cmds.bakeResults(
                camera,
                t=(int(start_frame), int(end_frame)),
                at=trs,
                simulation=True,
                preserveOutsideKeys=True,
                minimizeRotation=True,
            )
            self.log("Baking camera animation...")

        # --- Step 1: Bake animation to skeleton joints ---
        # Must happen first while constraints are still live.
        # Collect joints from rig_roots AND from skinCluster influences
        # on geo_roots.  The deformation skeleton may live outside the
        # rig hierarchy (e.g. GWoman_Joint_GRP vs GenWoman_rig_hrc).
        all_joints = []
        for root in (rig_roots or []):
            if cmds.objExists(root):
                joints = cmds.listRelatives(
                    root, allDescendents=True, type="joint",
                    fullPath=True
                ) or []
                all_joints.extend(joints)
                if cmds.objectType(root) == "joint":
                    all_joints.append(root)

        # Also discover joints that are skin influences on exported
        # geo but live outside the rig_roots hierarchy.
        skin_influence_roots = set()
        for geo_root in (geo_roots or []):
            if not cmds.objExists(geo_root):
                continue
            descendants = cmds.listRelatives(
                geo_root, allDescendents=True, type="transform",
                fullPath=True
            ) or []
            for desc in [cmds.ls(geo_root, long=True)[0]] + descendants:
                shapes = cmds.listRelatives(
                    desc, shapes=True, type="mesh", fullPath=True
                ) or []
                if not shapes:
                    continue
                history = cmds.listHistory(
                    desc, pruneDagObjects=True) or []
                for h in history:
                    if cmds.objectType(h) == "skinCluster":
                        influences = cmds.skinCluster(
                            h, query=True, influence=True
                        ) or []
                        # Resolve to long paths
                        influences = [
                            p for i in influences
                            for p in (cmds.ls(i, long=True) or [i])]
                        for inf in influences:
                            # Walk up to find the topmost joint or
                            # the first non-joint parent's child
                            current = inf
                            while True:
                                parent = cmds.listRelatives(
                                    current, parent=True,
                                    fullPath=True
                                )
                                if (not parent
                                        or cmds.objectType(
                                            parent[0]) != "joint"):
                                    break
                                current = parent[0]
                            skin_influence_roots.add(current)

        # Add any skin influence joints not already covered by
        # rig_roots
        rig_root_set = set()
        for root in (rig_roots or []):
            if cmds.objExists(root):
                rig_root_set.update(
                    cmds.ls(root, long=True) or [])
        added_from_skin = 0
        for inf_root in skin_influence_roots:
            # Check if this joint is already a descendant of
            # a rig_root
            already_covered = False
            long_inf = (cmds.ls(inf_root, long=True) or [inf_root])[0]
            for rr in rig_root_set:
                if long_inf.startswith(rr + "|"):
                    already_covered = True
                    break
            if not already_covered:
                extra_joints = cmds.listRelatives(
                    inf_root, allDescendents=True, type="joint",
                    fullPath=True
                ) or []
                if cmds.objectType(inf_root) == "joint":
                    extra_joints.append(
                        (cmds.ls(inf_root, long=True) or [inf_root])[0])
                all_joints.extend(extra_joints)
                added_from_skin += len(extra_joints)
        if added_from_skin:
            sys.stderr.write(
                "[ExportGenie]   Added {} joints from skin "
                "influences outside rig_roots\n".format(
                    added_from_skin))
            sys.stderr.write(
                "[ExportGenie]   Skin influence roots: "
                "{}\n".format(list(skin_influence_roots)))

        # De-duplicate preserving order
        seen = set()
        unique_joints = []
        for j in all_joints:
            if j not in seen:
                seen.add(j)
                unique_joints.append(j)
        all_joints = unique_joints

        # Also bake TRS on non-skinned mesh transforms under
        # geo_roots.  These may be driven by constraints, direct
        # connections, expressions, or parenting to animated
        # transforms (e.g. eyeball meshes following eye joints).
        # Baking captures the animation regardless of the driving
        # mechanism, so it survives constraint removal in Step 2.
        nonskinned_meshes = []
        for geo_root in (geo_roots or []):
            if not cmds.objExists(geo_root):
                continue
            descendants = cmds.listRelatives(
                geo_root, allDescendents=True, type="transform",
                fullPath=True
            ) or []
            for desc in [cmds.ls(geo_root, long=True)[0]] + descendants:
                if desc in skip_mesh_xforms:
                    continue
                shapes = cmds.listRelatives(
                    desc, shapes=True, type="mesh", fullPath=True
                ) or []
                if not shapes:
                    continue
                # Skip skinned meshes — they animate via skeleton
                history = cmds.listHistory(
                    desc, pruneDagObjects=True) or []
                if any(cmds.objectType(h) == "skinCluster"
                       for h in history):
                    continue
                nonskinned_meshes.append(desc)

        if nonskinned_meshes:
            sys.stderr.write(
                "[ExportGenie]   Baking {} non-skinned mesh "
                "transform(s)\n".format(len(nonskinned_meshes)))

            # --- PRE-BAKE DIAGNOSTICS ---
            for cm in nonskinned_meshes:
                short = cm.split("|")[-1]
                sys.stderr.write(
                    "[ExportGenie]   DIAG '{}' PRE-BAKE:\n".format(
                        short))
                # Parent
                par = cmds.listRelatives(
                    cm, parent=True, fullPath=True)
                sys.stderr.write(
                    "[ExportGenie]     parent: {}\n".format(
                        par[0] if par else "NONE"))
                # World-space position at start frame
                cmds.currentTime(int(start_frame), edit=True)
                ws_a = cmds.xform(
                    cm, query=True, worldSpace=True,
                    translation=True)
                sys.stderr.write(
                    "[ExportGenie]     world pos @ {}: "
                    "{:.3f} {:.3f} {:.3f}\n".format(
                        int(start_frame),
                        ws_a[0], ws_a[1], ws_a[2]))
                # World-space position at end frame
                cmds.currentTime(int(end_frame), edit=True)
                ws_b = cmds.xform(
                    cm, query=True, worldSpace=True,
                    translation=True)
                sys.stderr.write(
                    "[ExportGenie]     world pos @ {}: "
                    "{:.3f} {:.3f} {:.3f}\n".format(
                        int(end_frame),
                        ws_b[0], ws_b[1], ws_b[2]))
                # Connections on TRS channels
                for a in trs:
                    plug = "{}.{}".format(cm, a)
                    conns = cmds.listConnections(
                        plug, source=True, destination=False,
                        plugs=True, skipConversionNodes=True
                    ) or []
                    if conns:
                        for src in conns:
                            src_node = src.split(".")[0]
                            sys.stderr.write(
                                "[ExportGenie]     {}: {} "
                                "({})\n".format(
                                    a, src,
                                    cmds.nodeType(src_node)))

                # Check for constraint children
                for ctype in ["parentConstraint",
                              "pointConstraint",
                              "orientConstraint",
                              "aimConstraint"]:
                    cons = cmds.listRelatives(
                        cm, children=True, type=ctype,
                        fullPath=True
                    ) or []
                    for c in cons:
                        targets = cmds.parentConstraint(
                            c, query=True, targetList=True
                        ) if ctype == "parentConstraint" else []
                        sys.stderr.write(
                            "[ExportGenie]     constraint: {} "
                            "({}), targets: {}\n".format(
                                c.split("|")[-1], ctype,
                                targets))

            cmds.currentTime(int(start_frame), edit=True)

            # Unlock and bake TRS
            for cm in nonskinned_meshes:
                for a in trs:
                    try:
                        cmds.setAttr(
                            "{}.{}".format(cm, a),
                            lock=False, keyable=True, channelBox=True)
                    except Exception:
                        pass
            cmds.bakeResults(
                nonskinned_meshes,
                t=(int(start_frame), int(end_frame)),
                at=trs,
                simulation=True,
                preserveOutsideKeys=True,
                minimizeRotation=True,
            )

            # --- POST-BAKE DIAGNOSTICS ---
            for cm in nonskinned_meshes:
                short = cm.split("|")[-1]
                sys.stderr.write(
                    "[ExportGenie]   DIAG '{}' POST-BAKE:\n".format(
                        short))
                for a in trs:
                    plug = "{}.{}".format(cm, a)
                    conns = cmds.listConnections(
                        plug, source=True, destination=False,
                        plugs=True, skipConversionNodes=True
                    ) or []
                    if conns:
                        for src in conns:
                            src_node = src.split(".")[0]
                            sys.stderr.write(
                                "[ExportGenie]     {}: {} "
                                "({})\n".format(
                                    a, src,
                                    cmds.nodeType(src_node)))
                    else:
                        val = cmds.getAttr(plug)
                        sys.stderr.write(
                            "[ExportGenie]     {}: NO CONNECTION "
                            "(static={:.4f})\n".format(a, val))

            # Disconnect non-animCurve sources so baked curves
            # are the sole driver.  bakeResults may leave the
            # original constraint output connected alongside
            # the new anim curve — when Step 2 deletes the
            # constraint, the channel can lose its driver.
            disconnected_count = 0
            for cm in nonskinned_meshes:
                for a in trs:
                    plug = "{}.{}".format(cm, a)
                    conns = cmds.listConnections(
                        plug, source=True, destination=False,
                        plugs=True, skipConversionNodes=True
                    ) or []
                    for src_plug in conns:
                        src_node = src_plug.split(".")[0]
                        if cmds.nodeType(
                                src_node).startswith("animCurve"):
                            continue
                        try:
                            cmds.disconnectAttr(src_plug, plug)
                            disconnected_count += 1
                            sys.stderr.write(
                                "[ExportGenie]     disconnected: "
                                "{} -> {}\n".format(
                                    src_plug, plug))
                        except Exception as exc:
                            sys.stderr.write(
                                "[ExportGenie]     FAILED to "
                                "disconnect {} -> {}: {}\n".format(
                                    src_plug, plug, exc))

            # --- POST-DISCONNECT DIAGNOSTICS ---
            sys.stderr.write(
                "[ExportGenie]   Disconnected {} non-animCurve "
                "source(s)\n".format(disconnected_count))
            for cm in nonskinned_meshes:
                short = cm.split("|")[-1]
                sys.stderr.write(
                    "[ExportGenie]   DIAG '{}' POST-DISCONNECT"
                    ":\n".format(short))
                # Verify world pos still correct
                cmds.currentTime(int(start_frame), edit=True)
                ws_a = cmds.xform(
                    cm, query=True, worldSpace=True,
                    translation=True)
                cmds.currentTime(int(end_frame), edit=True)
                ws_b = cmds.xform(
                    cm, query=True, worldSpace=True,
                    translation=True)
                sys.stderr.write(
                    "[ExportGenie]     world pos @ {}: "
                    "{:.3f} {:.3f} {:.3f}\n".format(
                        int(start_frame),
                        ws_a[0], ws_a[1], ws_a[2]))
                sys.stderr.write(
                    "[ExportGenie]     world pos @ {}: "
                    "{:.3f} {:.3f} {:.3f}\n".format(
                        int(end_frame),
                        ws_b[0], ws_b[1], ws_b[2]))
                for a in trs:
                    plug = "{}.{}".format(cm, a)
                    conns = cmds.listConnections(
                        plug, source=True, destination=False,
                        plugs=True, skipConversionNodes=True
                    ) or []
                    if conns:
                        for src in conns:
                            src_node = src.split(".")[0]
                            sys.stderr.write(
                                "[ExportGenie]     {}: {} "
                                "({})\n".format(
                                    a, src,
                                    cmds.nodeType(src_node)))
                    else:
                        val = cmds.getAttr(plug)
                        sys.stderr.write(
                            "[ExportGenie]     {}: NO CONNECTION "
                            "(static={:.4f})\n".format(a, val))
            cmds.currentTime(int(start_frame), edit=True)
            sys.stderr.write(
                "[ExportGenie]   Non-skinned mesh bake complete\n")

        sys.stderr.write(
            "[ExportGenie] Step 1: Bake animation\n")
        if all_joints:
            sys.stderr.write(
                "[ExportGenie]   Found {} joints to bake\n".format(
                    len(all_joints)))
            for jnt in all_joints[:10]:
                sys.stderr.write(
                    "[ExportGenie]     {}\n".format(jnt))
            if len(all_joints) > 10:
                sys.stderr.write(
                    "[ExportGenie]     ... and {} more\n".format(
                        len(all_joints) - 10))
            self.log("Baking animation...")
            # Unlock TRS channels before baking
            for jnt in all_joints:
                for a in trs:
                    try:
                        cmds.setAttr(
                            "{}.{}".format(jnt, a),
                            lock=False, keyable=True, channelBox=True)
                    except Exception:
                        pass
            cmds.bakeResults(
                all_joints,
                t=(int(start_frame), int(end_frame)),
                at=trs,
                simulation=True,
                preserveOutsideKeys=True,
                minimizeRotation=True,
            )
            sys.stderr.write(
                "[ExportGenie]   Bake complete\n")
        else:
            sys.stderr.write(
                "[ExportGenie]   WARNING: No joints found under "
                "rig_roots!\n")

        # --- Step 2: Remove constraints ---
        constraint_types = [
            "parentConstraint", "pointConstraint", "orientConstraint",
            "aimConstraint", "scaleConstraint", "poleVectorConstraint",
        ]
        constraints_removed = 0
        for root in (rig_roots or []):
            if not cmds.objExists(root):
                continue
            for ctype in constraint_types:
                constraints = cmds.listRelatives(
                    root, allDescendents=True, type=ctype,
                    fullPath=True
                ) or []
                for c in constraints:
                    if cmds.objExists(c):
                        try:
                            cmds.delete(c)
                            constraints_removed += 1
                        except Exception:
                            pass
        if constraints_removed:
            self.log("Removing constraints...")

        # Disconnect non-animCurve sources on baked joints
        for jnt in all_joints:
            for a in trs:
                plug = "{}.{}".format(jnt, a)
                conns = cmds.listConnections(
                    plug, source=True, destination=False,
                    plugs=True, skipConversionNodes=True
                ) or []
                for src_plug in conns:
                    src_node = src_plug.split(".")[0]
                    if cmds.nodeType(src_node).startswith("animCurve"):
                        continue
                    try:
                        cmds.disconnectAttr(src_plug, plug)
                    except Exception:
                        pass

        # --- Step 3: Check joint scale ---
        for jnt in all_joints:
            cmds.currentTime(start_frame, edit=True)
            sx = cmds.getAttr("{}.scaleX".format(jnt))
            sy = cmds.getAttr("{}.scaleY".format(jnt))
            sz = cmds.getAttr("{}.scaleZ".format(jnt))
            if not (abs(sx - 1.0) < 1e-4
                    and abs(sy - 1.0) < 1e-4
                    and abs(sz - 1.0) < 1e-4):
                short = jnt.split("|")[-1].split(":")[-1]
                sys.stderr.write(
                    "[ExportGenie] WARNING: Joint '{}' has non-unit "
                    "scale ({:.3f}, {:.3f}, {:.3f})\n".format(
                        short, sx, sy, sz))

        # --- Step 4: Delete non-deformer history on meshes ---
        all_roots = list(geo_roots or []) + list(rig_roots or [])
        all_mesh_xforms = []
        for root in all_roots:
            if not cmds.objExists(root):
                sys.stderr.write(
                    "[ExportGenie] Step 4: root '{}' does not "
                    "exist!\n".format(root))
                continue
            descendants = cmds.listRelatives(
                root, allDescendents=True, type="transform",
                fullPath=True
            ) or []
            for desc in [root] + descendants:
                shapes = cmds.listRelatives(
                    desc, shapes=True, type="mesh", fullPath=True
                ) or []
                if shapes and desc not in all_mesh_xforms:
                    all_mesh_xforms.append(desc)

        sys.stderr.write(
            "[ExportGenie] Step 4: Delete non-deformer history\n")
        sys.stderr.write(
            "[ExportGenie]   Found {} mesh transforms\n".format(
                len(all_mesh_xforms)))
        # Log skinCluster status for each mesh
        for mx in all_mesh_xforms:
            history = cmds.listHistory(
                mx, pruneDagObjects=True) or []
            skins = [h for h in history
                     if cmds.objectType(h) == "skinCluster"]
            short = mx.split("|")[-1]
            if skins:
                for sc in skins:
                    inf_count = len(
                        cmds.skinCluster(
                            sc, query=True, influence=True
                        ) or [])
                    sys.stderr.write(
                        "[ExportGenie]     '{}' -> skinCluster '{}' "
                        "({} influences)\n".format(
                            short, sc, inf_count))
            else:
                sys.stderr.write(
                    "[ExportGenie]     '{}' -> no skinCluster\n".format(
                        short))

        history_deleted = 0
        baked_mesh_set = set(
            nonskinned_meshes) if nonskinned_meshes else set()
        for mesh_xform in all_mesh_xforms:
            if mesh_xform in skip_mesh_xforms:
                continue
            if mesh_xform in baked_mesh_set:
                continue
            try:
                cmds.bakePartialHistory(
                    mesh_xform, prePostDeformers=True)
                history_deleted += 1
            except Exception:
                pass
        if history_deleted:
            self.log("Cleaning up history...")

        # Verify skinClusters survived Step 4
        sys.stderr.write(
            "[ExportGenie] Step 4 POST-CHECK: skinCluster status "
            "after history bake\n")
        for mx in all_mesh_xforms:
            history = cmds.listHistory(
                mx, pruneDagObjects=True) or []
            skins = [h for h in history
                     if cmds.objectType(h) == "skinCluster"]
            short = mx.split("|")[-1]
            if skins:
                for sc in skins:
                    inf_count = len(
                        cmds.skinCluster(
                            sc, query=True, influence=True
                        ) or [])
                    sys.stderr.write(
                        "[ExportGenie]     '{}' -> skinCluster '{}' "
                        "({} influences) OK\n".format(
                            short, sc, inf_count))
            else:
                sys.stderr.write(
                    "[ExportGenie]     '{}' -> LOST skinCluster "
                    "after Step 4!\n".format(short))

        # --- Step 5: Freeze transforms on non-skinned non-joint geo ---
        # Build set of meshes with baked anim curves (from the
        # non-skinned mesh bake above) so we don't freeze them.
        baked_mesh_set = set(nonskinned_meshes) if nonskinned_meshes else set()
        transforms_frozen = 0
        for mesh_xform in all_mesh_xforms:
            if mesh_xform in skip_mesh_xforms:
                continue
            if mesh_xform in baked_mesh_set:
                continue
            # Skip skinned meshes
            history = cmds.listHistory(
                mesh_xform, pruneDagObjects=True
            ) or []
            has_skin = any(
                cmds.objectType(h) == "skinCluster" for h in history)
            if has_skin:
                continue
            # Skip transforms with child joints
            child_joints = cmds.listRelatives(
                mesh_xform, allDescendents=True, type="joint"
            ) or []
            if child_joints:
                continue
            try:
                cmds.makeIdentity(
                    mesh_xform, apply=True,
                    translate=True, rotate=True, scale=True, normal=0)
                transforms_frozen += 1
            except Exception:
                pass
        if transforms_frozen:
            self.log("Freezing transforms...")

        # Verify skinClusters survived Step 5
        sys.stderr.write(
            "[ExportGenie] Step 5 POST-CHECK: skinCluster status "
            "after freeze transforms\n")
        sc_after_5 = cmds.ls(type="skinCluster") or []
        sys.stderr.write(
            "[ExportGenie]   Total skinClusters in scene: "
            "{}\n".format(len(sc_after_5)))
        for sc in sc_after_5:
            inf_count = len(
                cmds.skinCluster(
                    sc, query=True, influence=True) or [])
            geo = cmds.skinCluster(
                sc, query=True, geometry=True) or []
            sys.stderr.write(
                "[ExportGenie]     '{}': {} influences, "
                "geo={}\n".format(sc, inf_count, geo))

        # --- Step 6: Strip namespaces ---
        all_ns = cmds.namespaceInfo(
            listOnlyNamespaces=True, recurse=True
        ) or []
        skip_ns = {"UI", "shared"}
        all_ns = [ns for ns in all_ns if ns not in skip_ns]
        # Sort longest-first for nested namespaces
        all_ns.sort(key=len, reverse=True)

        namespaces_stripped = 0
        for ns in all_ns:
            try:
                ns_contents = cmds.namespaceInfo(
                    ns, listNamespace=True
                ) or []
                has_referenced = False
                for node in ns_contents:
                    if cmds.objExists(node):
                        try:
                            if cmds.referenceQuery(
                                    node, isNodeReferenced=True):
                                has_referenced = True
                                break
                        except RuntimeError:
                            pass
                if has_referenced:
                    sys.stderr.write(
                        "[ExportGenie] Skipping namespace "
                        "'{}' (referenced)\n".format(ns))
                    continue
                cmds.namespace(
                    removeNamespace=ns, mergeNamespaceWithRoot=True)
                namespaces_stripped += 1
            except Exception:
                pass
        if namespaces_stripped:
            self.log("Stripping namespaces...")

        # Verify skinClusters survived Step 6
        sys.stderr.write(
            "[ExportGenie] Step 6 POST-CHECK: skinCluster status "
            "after namespace strip\n")
        sc_after_6 = cmds.ls(type="skinCluster") or []
        sys.stderr.write(
            "[ExportGenie]   Total skinClusters in scene: "
            "{}\n".format(len(sc_after_6)))
        for sc in sc_after_6:
            inf_count = len(
                cmds.skinCluster(
                    sc, query=True, influence=True) or [])
            geo = cmds.skinCluster(
                sc, query=True, geometry=True) or []
            sys.stderr.write(
                "[ExportGenie]     '{}': {} influences, "
                "geo={}\n".format(sc, inf_count, geo))

        # --- Step 7: Delete ALL dagPose nodes ---
        # dagPose (bindPose) nodes store the rest-pose of each
        # influence and every ancestor transform must be registered.
        # Complex rigs often have incomplete dagPose definitions that
        # cause the FBX exporter to fail silently (meshes export but
        # don't animate).  Patching existing dagPose nodes with
        # addToPose can corrupt the stored bind pose.
        #
        # The safest approach: delete every dagPose in the scene.
        # The FBX plugin's built-in bake (FBXExportBakeComplexAnimation)
        # will re-evaluate animation from the baked anim curves on
        # joints — it does not need a dagPose to do this.  Removing
        # dagPose eliminates "not part of the BindPose definition"
        # errors entirely.
        sys.stderr.write(
            "[ExportGenie] Step 7: Delete dagPose nodes\n")
        dag_poses = cmds.ls(type="dagPose") or []
        if dag_poses:
            sys.stderr.write(
                "[ExportGenie]   Deleting {} dagPose node(s): "
                "{}\n".format(len(dag_poses), dag_poses))
            cmds.delete(dag_poses)
            self.log("Removing bind pose nodes...")
        else:
            sys.stderr.write(
                "[ExportGenie]   No dagPose nodes found\n")

    def detect_vertex_anim_meshes(self, geo_roots, start_frame, end_frame):
        """Detect meshes with per-vertex animation under geo_roots.

        Samples 3 vertex positions at start_frame vs end_frame to find
        meshes with real vertex deformation (vs. AlembicNode only driving
        TRS).  Read-only — does not modify the scene.

        Args:
            geo_roots: list of root transforms to search under.
            start_frame: first frame to sample.
            end_frame: last frame to sample.

        Returns:
            set of long DAG paths (mesh transforms) with vertex animation.
        """
        geo_roots = geo_roots or []
        # Collect mesh transforms under all roots
        mesh_xforms = []
        for root in geo_roots:
            if not cmds.objExists(root):
                continue
            descendants = cmds.listRelatives(
                root, allDescendents=True, type="transform",
                fullPath=True
            ) or []
            for desc in [cmds.ls(root, long=True)[0]] + descendants:
                shapes = cmds.listRelatives(
                    desc, shapes=True, type="mesh", fullPath=True
                ) or []
                # Filter out intermediate (orig) shapes
                shapes = [
                    s for s in shapes
                    if not cmds.getAttr(s + ".intermediateObject")
                ]
                if shapes and desc not in mesh_xforms:
                    mesh_xforms.append(desc)

        # Exclude meshes driven by a skinCluster — their vertices move
        # due to skeletal deformation, not Alembic vertex caching.
        skinned = set()
        for xform in mesh_xforms:
            history = cmds.listHistory(
                xform, pruneDagObjects=True) or []
            if any(cmds.objectType(h) == "skinCluster"
                   for h in history):
                skinned.add(xform)
        mesh_xforms = [m for m in mesh_xforms if m not in skinned]

        vertex_anim_set = set()
        if not mesh_xforms:
            return vertex_anim_set

        original_time = cmds.currentTime(query=True)
        sample_frame_a = int(start_frame)
        sample_frame_b = int(end_frame)

        # Collect positions at frame A
        cmds.currentTime(sample_frame_a, edit=True)
        positions_a = {}  # {long_name: (shape, indices, [pos, ...])}
        for xform in mesh_xforms:
            shapes = cmds.listRelatives(
                xform, shapes=True, type="mesh", fullPath=True
            ) or []
            for shp in shapes:
                try:
                    if cmds.getAttr(shp + ".intermediateObject"):
                        continue
                except Exception:
                    pass
                vtx_count = cmds.polyEvaluate(shp, vertex=True)
                if not vtx_count:
                    continue
                indices = list(set(
                    [0, vtx_count // 2, max(0, vtx_count - 1)]))
                pts = []
                for idx in indices:
                    pts.append(cmds.pointPosition(
                        "{}.vtx[{}]".format(shp, idx), local=True))
                positions_a[xform] = (shp, indices, pts)
                break  # one non-intermediate shape is enough

        # Collect positions at frame B and compare
        if sample_frame_a != sample_frame_b:
            cmds.currentTime(sample_frame_b, edit=True)
            for long_name, (shp, indices, pts_a) in positions_a.items():
                found = False
                for i, idx in enumerate(indices):
                    pos_b = cmds.pointPosition(
                        "{}.vtx[{}]".format(shp, idx), local=True)
                    for c in range(3):
                        if abs(pts_a[i][c] - pos_b[c]) > 1e-5:
                            vertex_anim_set.add(long_name)
                            found = True
                            break
                    if found:
                        break

        cmds.currentTime(original_time, edit=True)
        return vertex_anim_set

    def prepare_face_track_for_export(self, picked_nodes, start_frame,
                                       end_frame):
        """Traverse picked groups, classify descendants, and prepare for FBX.

        For each picked node, recursively finds leaf transforms and classifies
        them as vertex-animated (Alembic), anim-curve-driven, or static.
        Vertex-animated meshes are converted to blendshapes. Anim-curve
        transforms are baked in-place.

        Returns:
            dict with keys: select_for_export, base_meshes,
                vertex_anim_count, anim_curve_count, static_count
        """
        select_for_export = []
        base_meshes = []
        vertex_anim_count = 0
        anim_curve_count = 0
        static_count = 0

        def _collect_leaves(node):
            """Recursively collect leaf transforms (meshes or animated xforms)."""
            leaves = []
            mesh_shapes = cmds.listRelatives(
                node, shapes=True, type="mesh", fullPath=True
            ) or []
            # Filter out intermediate (orig) shapes
            mesh_shapes = [
                s for s in mesh_shapes
                if not cmds.getAttr(s + ".intermediateObject")
            ]

            if mesh_shapes:
                leaves.append(node)
            else:
                children = cmds.listRelatives(
                    node, children=True, type="transform", fullPath=True
                ) or []
                if children:
                    for child in children:
                        leaves.extend(_collect_leaves(child))
                else:
                    # Non-mesh leaf (locator, null, etc.) — include if animated
                    leaves.append(node)
            return leaves

        # Phase 1: collect all leaf transforms
        all_leaves = []
        for picked in picked_nodes:
            if not cmds.objExists(picked):
                sys.stderr.write(
                    "[ExportGenie] '{}' not found, "
                    "skipping.\n".format(picked))
                continue
            all_leaves.extend(_collect_leaves(picked))

        # De-duplicate preserving order
        seen = set()
        unique_leaves = []
        for leaf in all_leaves:
            long_name = cmds.ls(leaf, long=True)[0]
            if long_name not in seen:
                seen.add(long_name)
                unique_leaves.append(leaf)

        self.log("Classifying geometry..."
                 )
        sys.stderr.write(
            "[ExportGenie] Found {} leaf transforms to classify.\n".format(
            len(unique_leaves)))

        # Phase 2a: batch vertex-animation detection
        vertex_anim_set = self.detect_vertex_anim_meshes(
            picked_nodes, start_frame, end_frame)

        # Phase 2b: classify and process each leaf
        for leaf in unique_leaves:
            long_name = cmds.ls(leaf, long=True)[0]
            short_name = leaf.split("|")[-1]

            if long_name in vertex_anim_set:
                conv = self.convert_abc_to_blendshape(
                    leaf, start_frame, end_frame)
                select_for_export.append(conv["base_mesh"])
                base_meshes.append(conv["base_mesh"])
                vertex_anim_count += 1

            elif self._has_driven_transforms(leaf):
                self._bake_transform_curves(leaf, start_frame, end_frame)
                select_for_export.append(leaf)
                anim_curve_count += 1

            else:
                select_for_export.append(leaf)
                static_count += 1

        self.log(
            "Classification: {} blendshape, {} animated, "
            "{} static".format(
                vertex_anim_count, anim_curve_count, static_count))

        return {
            "select_for_export": select_for_export,
            "base_meshes": base_meshes,
            "vertex_anim_count": vertex_anim_count,
            "anim_curve_count": anim_curve_count,
            "static_count": static_count,
        }

    def export_playblast(self, file_path, camera, start_frame, end_frame,
                         camera_track_mode=False, matchmove_geo=None,
                         checker_scale=8, checker_color=None,
                         checker_opacity=70, raw_playblast=False,
                         render_raw_srgb=True,
                         wireframe_shader=False,
                         wireframe_shader_geo=None,
                         msaa_16=False,
                         far_clip=800000,
                         png_mode=False,
                         mp4_mode=False,
                         mp4_output=None,
                         show_hud=False,
                         composite_plate_path=None,
                         composite_color_path=None,
                         composite_matte_path=None,
                         composite_tmp_dir=None):
        """Export a QC playblast at 1920x1080.

        Supports H.264 .mov (via QuickTime), PNG image sequence, or
        H.264 .mp4 (via bundled ffmpeg on Windows).

        Args:
            camera_track_mode: If True, applies Camera Track viewport
                overrides (wireframe, AA).
            matchmove_geo: Optional list of geo root transforms for the
                Matchmove tab.  When provided, forces display layers
                visible, isolates only these geo roots, sets smooth
                shaded display, and applies a UV checker overlay.
            raw_playblast: If True, skips ALL viewport modifications.
                The playblast uses the user's current VP2.0 settings
                — only the camera is switched to cam_main.
            wireframe_shader: If True, applies a useBackground shader
                to all meshes under wireframe_shader_geo and sets the
                viewport to wireframe-on-shaded mode.
            wireframe_shader_geo: List of geo root transforms (or single
                node) whose descendant meshes receive the useBackground
                shader.
            png_mode: If True, exports PNG image sequence instead of
                H.264 .mov.  Skips QuickTime validation.
            mp4_mode: If True, playblasts to temp PNG sequence then
                encodes to H.264 .mp4 via bundled ffmpeg (Windows only).
            mp4_output: Full path to the output .mp4 file.  Required
                when mp4_mode is True.
        """
        matchmove_geo = [
            g for g in (matchmove_geo or []) if g and cmds.objExists(g)
        ]
        try:
            # Validate format availability
            pb_format = None
            if mp4_mode:
                pb_format = "image"
                if not self._find_ffmpeg():
                    if sys.platform == "win32":
                        fix_msg = (
                            "How to fix:\n"
                            "Re-install Export Genie by dragging "
                            "the .py file (from the folder "
                            "containing bin/) into Maya's "
                            "viewport.\n\n"
                            "Expected location:\n"
                            "{}".format(
                                os.path.join(
                                    os.path.dirname(
                                        os.path.abspath(__file__)),
                                    "bin", "win", "ffmpeg.exe")))
                    else:
                        fix_msg = (
                            "How to fix:\n"
                            "Install ffmpeg via your system "
                            "package manager:\n"
                            "  macOS:  brew install ffmpeg\n"
                            "  Linux:  sudo apt install ffmpeg")
                    cmds.confirmDialog(
                        title="Cannot Create QC Movie",
                        message=(
                            "Export Genie {}\n\n"
                            "ffmpeg was not found.\n\n"
                            "The H.264 .mp4 format requires "
                            "ffmpeg.\n\n"
                            "{}".format(TOOL_VERSION, fix_msg)),
                        button=["OK"],
                    )
                    return False
                self.log("Checking for ffmpeg...")
            elif png_mode:
                pb_format = "image"
                self.log("Setting up viewport...")
            else:
                pb_format, diag = self._validate_playblast_format()
                self.log("Setting up viewport...")

                if pb_format is None:
                    # Build a clear, non-technical message
                    if sys.platform == "win32":
                        qt_info = self._check_quicktime_windows()
                        if not qt_info["registry_found"]:
                            msg = (
                                "QuickTime is not installed.\n\n"
                                "The QC movie export needs Apple QuickTime "
                                "to create .mov files.\n\n"
                                "How to fix:\n"
                                "  1. Download QuickTime 7.7.9 for Windows "
                                "from apple.com\n"
                                "  2. Run the installer and make sure "
                                "'QuickTime Essentials' is checked\n"
                                "  3. Close and reopen Maya")
                        elif not qt_info["qts_found"]:
                            msg = (
                                "QuickTime is only partially installed.\n\n"
                                "Maya found a QuickTime entry on this "
                                "machine, but the core files are missing "
                                "from disk.\n\n"
                                "How to fix:\n"
                                "  1. Uninstall QuickTime from "
                                "Add/Remove Programs\n"
                                "  2. Reinstall QuickTime 7.7.9 for "
                                "Windows\n"
                                "  3. Close and reopen Maya")
                        else:
                            msg = (
                                "QuickTime is installed, but Maya cannot "
                                "use it.\n\n"
                                "The QuickTime files are on disk but Maya "
                                "does not see the .mov format.\n\n"
                                "How to fix:\n"
                                "  1. Close and reopen Maya (this is "
                                "required after installing QuickTime)\n"
                                "  2. If that doesn't work, uninstall "
                                "QuickTime, reinstall it using the "
                                "'Full' option, and reopen Maya")
                    else:
                        msg = (
                            "No .mov format is available.\n\n"
                            "AVFoundation should be built-in on macOS. "
                            "Go to Windows > Settings/Preferences > "
                            "Plug-in Manager and check that media "
                            "plugins are loaded.")
                    cmds.confirmDialog(
                        title="Cannot Create QC Movie",
                        message="Export Genie {}\n\n{}".format(
                            TOOL_VERSION, msg),
                        button=["OK"],
                    )
                    return False

            # Find a visible model panel for the playblast.
            model_panel = None
            for panel in (cmds.getPanel(visiblePanels=True) or []):
                if cmds.getPanel(typeOf=panel) == "modelPanel":
                    model_panel = panel
                    break
            if not model_panel:
                panels = cmds.getPanel(type="modelPanel") or []
                if panels:
                    model_panel = panels[0]

            # Switch camera
            original_cam = None
            original_pan_zoom = None
            if camera and model_panel:
                original_cam = cmds.modelPanel(
                    model_panel, query=True, camera=True
                )
                cmds.lookThru(model_panel, camera)

            # Disable 2D pan/zoom — animation aid, not for QC renders.
            # Extend far clipping plane so distant geometry is visible.
            original_far_clip = None
            if camera:
                cam_shapes = cmds.listRelatives(
                    camera, shapes=True, type="camera") or []
                if cam_shapes:
                    try:
                        original_pan_zoom = cmds.getAttr(
                            cam_shapes[0] + ".panZoomEnabled")
                        cmds.setAttr(
                            cam_shapes[0] + ".panZoomEnabled", False)
                    except Exception:
                        pass
                    try:
                        original_far_clip = cmds.getAttr(
                            cam_shapes[0] + ".farClipPlane")
                        cmds.setAttr(
                            cam_shapes[0] + ".farClipPlane",
                            far_clip)
                    except Exception:
                        pass

            # Hide the grid for all QC renders.
            original_grid = None
            if model_panel:
                try:
                    original_grid = cmds.modelEditor(
                        model_panel, query=True, grid=True)
                    cmds.modelEditor(
                        model_panel, edit=True, grid=False)
                except Exception:
                    pass

            # Clear selection so no highlight appears in the playblast
            original_sel = cmds.ls(selection=True)
            cmds.select(clear=True)

            # --- HUD overlay for frame / focal length ---
            original_hud_vis = {}
            hud_names_to_remove = []
            original_font_mode = None
            original_font_size = None

            if show_hud:
                # Bump VP2.0 HUD font to max (24) for readability
                try:
                    original_font_mode = cmds.displayPref(
                        query=True, fontSettingMode=True)
                    original_font_size = cmds.displayPref(
                        query=True, defaultFontSize=True)
                    cmds.displayPref(fontSettingMode=2,
                                     defaultFontSize=24)
                    cmds.refresh(force=True)
                except Exception:
                    pass

                # Save and hide all existing HUDs
                existing_huds = (
                    cmds.headsUpDisplay(listHeadsUpDisplays=True) or [])
                for hud_name in existing_huds:
                    try:
                        original_hud_vis[hud_name] = cmds.headsUpDisplay(
                            hud_name, query=True, visible=True)
                        cmds.headsUpDisplay(
                            hud_name, edit=True, visible=False)
                    except Exception:
                        pass

                # Resolve camera shape for focal length
                hud_cam_shape = None
                if camera:
                    cam_shapes = cmds.listRelatives(
                        camera, shapes=True, type="camera") or []
                    if cam_shapes:
                        hud_cam_shape = cam_shapes[0]

                # Frame number HUD (bottom-center)
                hud_frame = "ExportGenie_FrameHUD"
                if cmds.headsUpDisplay(hud_frame, exists=True):
                    cmds.headsUpDisplay(hud_frame, remove=True)
                cmds.headsUpDisplay(
                    hud_frame, section=7,
                    block=cmds.headsUpDisplay(nextFreeBlock=7),
                    label="Frame:",
                    labelFontSize="large",
                    dataFontSize="large",
                    blockSize="medium",
                    command=lambda: int(cmds.currentTime(query=True)),
                    attachToRefresh=True,
                )
                hud_names_to_remove.append(hud_frame)

                # Focal length HUD (bottom-right)
                if hud_cam_shape:
                    hud_fl = "ExportGenie_FocalLengthHUD"
                    if cmds.headsUpDisplay(hud_fl, exists=True):
                        cmds.headsUpDisplay(hud_fl, remove=True)
                    fl_shape = hud_cam_shape
                    cmds.headsUpDisplay(
                        hud_fl, section=9,
                        block=cmds.headsUpDisplay(nextFreeBlock=9),
                        label="FL:", labelFontSize="large",
                        dataFontSize="large", blockSize="medium",
                        command=lambda: cmds.getAttr(
                            fl_shape + ".focalLength"),
                        attachToRefresh=True,
                        decimalPrecision=1,
                    )
                    hud_names_to_remove.append(hud_fl)

            # Playblast colour management — set once and persist.
            # When render_raw_srgb is True we ensure the Preferences >
            # Color Management > Playblast view transform is Raw (sRGB).
            # The change is intentionally left in the scene file so it
            # is NOT part of the undo block and not restored afterwards.

            # --- Camera Track overrides (wireframe + AA) ---
            original_display = None
            original_aa = None
            original_msaa_count = None
            original_smooth_wire = None
            original_editor_vis = {}
            original_ct_wos = None
            original_ct_shading = {}
            ct_bg_shader_nodes = []

            if camera_track_mode and model_panel and not raw_playblast:
                if wireframe_shader and wireframe_shader_geo:
                    # Wireframe-on-shaded with useBackground shader:
                    # meshes become transparent (showing the camera
                    # plate) with wireframe edges drawn on top.
                    original_display = cmds.modelEditor(
                        model_panel, query=True,
                        displayAppearance=True)
                    cmds.modelEditor(
                        model_panel, edit=True,
                        displayAppearance="smoothShaded")
                    original_ct_wos = cmds.modelEditor(
                        model_panel, query=True,
                        wireframeOnShaded=True)
                    cmds.modelEditor(
                        model_panel, edit=True,
                        wireframeOnShaded=True)

                    # Create useBackground shader
                    bg_shader = cmds.shadingNode(
                        "useBackground", asShader=True,
                        name="mme_ctBgShader_mtl")
                    ct_bg_shader_nodes.append(bg_shader)
                    bg_sg = cmds.sets(
                        renderable=True, noSurfaceShader=True,
                        empty=True, name="mme_ctBgShader_SG")
                    ct_bg_shader_nodes.append(bg_sg)
                    cmds.connectAttr(
                        "{}.outColor".format(bg_shader),
                        "{}.surfaceShader".format(bg_sg),
                        force=True)

                    # Collect meshes and save original shading
                    ct_meshes = []
                    wf_geo_list = wireframe_shader_geo or []
                    if isinstance(wf_geo_list, str):
                        wf_geo_list = [wf_geo_list]
                    for geo_node in wf_geo_list:
                        if geo_node and cmds.objExists(geo_node):
                            descendants = cmds.listRelatives(
                                geo_node, allDescendents=True,
                                type="mesh", fullPath=True) or []
                            for m in descendants:
                                try:
                                    if not cmds.getAttr(
                                            m + ".intermediateObject"):
                                        ct_meshes.append(m)
                                except Exception:
                                    pass
                    ct_transforms = list(set(
                        cmds.listRelatives(
                            ct_meshes, parent=True,
                            fullPath=True) or []
                    )) if ct_meshes else []

                    for mesh in ct_meshes:
                        try:
                            sgs = cmds.listConnections(
                                mesh, type="shadingEngine") or []
                            if sgs:
                                original_ct_shading[mesh] = sgs[0]
                        except Exception:
                            pass

                    # Assign useBackground shader
                    if ct_transforms:
                        cmds.select(ct_transforms, replace=True)
                        cmds.hyperShade(assign=bg_shader)
                        cmds.select(clear=True)
                else:
                    # Default camera track mode: pure wireframe display
                    original_display = cmds.modelEditor(
                        model_panel, query=True,
                        displayAppearance=True)
                    if original_display != "wireframe":
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayAppearance="wireframe")

                # Anti-aliasing
                try:
                    original_aa = cmds.getAttr(
                        "hardwareRenderingGlobals.multiSampleEnable")
                    cmds.setAttr(
                        "hardwareRenderingGlobals.multiSampleEnable", True)
                except Exception:
                    pass
                try:
                    original_msaa_count = cmds.getAttr(
                        "hardwareRenderingGlobals.multiSampleCount")
                    cmds.setAttr(
                        "hardwareRenderingGlobals.multiSampleCount",
                        16 if msaa_16 else 8)
                except Exception:
                    pass
                try:
                    original_smooth_wire = cmds.modelEditor(
                        model_panel, query=True, smoothWireframe=True)
                    cmds.modelEditor(
                        model_panel, edit=True, smoothWireframe=True)
                except Exception:
                    pass

                # Ensure geometry types are visible
                for flag in ("polymeshes", "nurbsSurfaces",
                             "subdivSurfaces"):
                    try:
                        original_editor_vis[flag] = cmds.modelEditor(
                            model_panel, query=True, **{flag: True})
                        cmds.modelEditor(
                            model_panel, edit=True, **{flag: True})
                    except Exception:
                        pass

            # --- Matchmove overrides ---
            original_layer_vis = {}
            original_layer_playback = {}
            original_isolate_state = False
            original_mm_display = None
            original_mm_wos = None
            original_mm_smooth_wire = None
            original_mm_aa = None
            original_mm_msaa_count = None
            original_mm_motion_blur = None
            original_shading = {}
            checker_nodes = []
            original_display_textures = None
            original_display_lights = None
            original_use_default_mtl = None
            original_image_plane = None
            original_nurbs_curves = None
            mm_meshes = []
            composite_rendered = False

            if matchmove_geo and model_panel and not raw_playblast:
                # 1. Force all display layers visible so nothing is
                #    hidden by layer overrides during the playblast.
                for layer in (cmds.ls(type="displayLayer") or []):
                    if layer == "defaultLayer":
                        continue
                    try:
                        original_layer_vis[layer] = cmds.getAttr(
                            layer + ".visibility")
                        cmds.setAttr(layer + ".visibility", True)
                    except Exception:
                        pass
                    try:
                        original_layer_playback[layer] = cmds.getAttr(
                            layer + ".hideOnPlayback")
                        cmds.setAttr(layer + ".hideOnPlayback", False)
                    except Exception:
                        pass

                # 2. Isolate select — show only the animated geo roots,
                #    the camera, and its image planes.
                original_isolate_state = cmds.isolateSelect(
                    model_panel, query=True, state=True)
                cmds.isolateSelect(model_panel, state=True)
                for geo_root in matchmove_geo:
                    cmds.isolateSelect(
                        model_panel, addDagObject=geo_root)
                # Add the camera and its image planes so the
                # plate sequence is visible in the background.
                if camera:
                    try:
                        cmds.isolateSelect(
                            model_panel, addDagObject=camera)
                    except Exception:
                        pass
                    cam_shapes = cmds.listRelatives(
                        camera, shapes=True, type="camera") or []
                    for cs in cam_shapes:
                        img_planes = cmds.listConnections(
                            cs + ".imagePlane",
                            type="imagePlane") or []
                        for ip in img_planes:
                            try:
                                cmds.isolateSelect(
                                    model_panel, addDagObject=ip)
                            except Exception:
                                pass

                # 3. Enable image planes on the viewport
                original_image_plane = cmds.modelEditor(
                    model_panel, query=True, imagePlane=True)
                cmds.modelEditor(
                    model_panel, edit=True, imagePlane=True)

                # 3b. NURBS curves — hide all except QC_head_GRP
                original_nurbs_curves = cmds.modelEditor(
                    model_panel, query=True, nurbsCurves=True)
                if (cmds.objExists("QC_head_GRP")
                        and cmds.listRelatives(
                            "QC_head_GRP", allDescendents=True,
                            type="nurbsCurve")):
                    cmds.modelEditor(
                        model_panel, edit=True, nurbsCurves=True)
                    cmds.isolateSelect(
                        model_panel, addDagObject="QC_head_GRP")
                else:
                    cmds.modelEditor(
                        model_panel, edit=True, nurbsCurves=False)

                # 4. Smooth shaded, no wireframe overlay
                original_mm_display = cmds.modelEditor(
                    model_panel, query=True, displayAppearance=True)
                cmds.modelEditor(
                    model_panel, edit=True,
                    displayAppearance="smoothShaded")
                original_mm_wos = cmds.modelEditor(
                    model_panel, query=True, wireframeOnShaded=True)
                cmds.modelEditor(
                    model_panel, edit=True, wireframeOnShaded=False)

                # 5. Smooth wireframe + MSAA 16 + motion blur
                try:
                    original_mm_smooth_wire = cmds.modelEditor(
                        model_panel, query=True, smoothWireframe=True)
                    cmds.modelEditor(
                        model_panel, edit=True, smoothWireframe=True)
                except Exception:
                    pass
                try:
                    original_mm_aa = cmds.getAttr(
                        "hardwareRenderingGlobals.multiSampleEnable")
                    cmds.setAttr(
                        "hardwareRenderingGlobals.multiSampleEnable", True)
                except Exception:
                    pass
                try:
                    original_mm_msaa_count = cmds.getAttr(
                        "hardwareRenderingGlobals.multiSampleCount")
                    cmds.setAttr(
                        "hardwareRenderingGlobals.multiSampleCount",
                        16 if msaa_16 else 8)
                except Exception:
                    pass
                try:
                    original_mm_motion_blur = cmds.getAttr(
                        "hardwareRenderingGlobals.motionBlurEnable")
                    cmds.setAttr(
                        "hardwareRenderingGlobals.motionBlurEnable", True)
                except Exception:
                    pass

                # 6. Collect meshes and save original shading
                try:
                    for geo_root in matchmove_geo:
                        descendants = cmds.listRelatives(
                            geo_root, allDescendents=True,
                            type="mesh", fullPath=True) or []
                        for m in descendants:
                            try:
                                if not cmds.getAttr(
                                        m + ".intermediateObject"):
                                    mm_meshes.append(m)
                            except Exception:
                                pass
                    mm_transforms = list(set(
                        cmds.listRelatives(
                            mm_meshes, parent=True,
                            fullPath=True) or []
                    )) if mm_meshes else []

                    sys.stderr.write(
                        "[MME] Composite: {} meshes, "
                        "{} transforms found\n".format(
                            len(mm_meshes), len(mm_transforms)))

                    for mesh in mm_meshes:
                        try:
                            sgs = cmds.listConnections(
                                mesh, type="shadingEngine") or []
                            if sgs:
                                original_shading[mesh] = sgs[0]
                        except Exception:
                            pass

                    # Check ffmpeg + composite paths for multi-pass
                    use_composite = (
                        bool(self._find_ffmpeg())
                        and composite_plate_path
                        and composite_color_path
                        and composite_matte_path)
                    if not use_composite:
                        sys.stderr.write(
                            "[MME] ffmpeg not found — falling back "
                            "to single-pass checker overlay\n")
                        self.log(
                            "ffmpeg not found — using single-pass "
                            "checker overlay.")

                    if use_composite:
                        # --- Multi-pass composite mode ---
                        # Save original background colors
                        original_bg = cmds.displayRGBColor(
                            "background", query=True)
                        original_bg_top = cmds.displayRGBColor(
                            "backgroundTop", query=True)
                        original_bg_bottom = cmds.displayRGBColor(
                            "backgroundBottom", query=True)
                        original_gradient = cmds.displayPref(
                            query=True, displayGradient=True)

                        # Disable useDefaultMaterial
                        original_use_default_mtl = cmds.modelEditor(
                            model_panel, query=True,
                            useDefaultMaterial=True)
                        cmds.modelEditor(
                            model_panel, edit=True,
                            useDefaultMaterial=False)

                        # Enable textured display with default light
                        original_display_textures = cmds.modelEditor(
                            model_panel, query=True,
                            displayTextures=True)
                        original_display_lights = cmds.modelEditor(
                            model_panel, query=True,
                            displayLights=True)
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayTextures=True,
                            displayLights="default")

                        # Create temp directories
                        composite_plate_dir = os.path.dirname(
                            composite_plate_path)
                        composite_color_dir = os.path.dirname(
                            composite_color_path)
                        composite_matte_dir = os.path.dirname(
                            composite_matte_path)
                        for d in (composite_plate_dir,
                                  composite_color_dir,
                                  composite_matte_dir):
                            if not os.path.exists(d):
                                os.makedirs(d)

                        # --- Pass 1: Plate (background only) ---
                        self.log("Rendering plate pass...")
                        cmds.modelEditor(
                            model_panel, edit=True,
                            imagePlane=True, polymeshes=False,
                            nurbsSurfaces=False,
                            subdivSurfaces=False)
                        cmds.refresh(force=True)
                        cmds.playblast(
                            filename=composite_plate_path,
                            format="image",
                            compression="png",
                            startTime=start_frame,
                            endTime=end_frame,
                            forceOverwrite=True,
                            sequenceTime=False,
                            clearCache=True,
                            viewer=False,
                            showOrnaments=show_hud,
                            framePadding=4,
                            percent=100,
                            quality=100,
                            widthHeight=[1920, 1080],
                        )

                        # --- Pass 2: Solid Color Mesh ---
                        self.log("Rendering color pass...")
                        # Black background, no gradient
                        cmds.displayRGBColor(
                            "background", 0, 0, 0)
                        cmds.displayRGBColor(
                            "backgroundTop", 0, 0, 0)
                        cmds.displayRGBColor(
                            "backgroundBottom", 0, 0, 0)
                        cmds.displayPref(displayGradient=False)

                        # Flat lighting — no viewport shading or
                        # shadows so self-shadowing doesn't affect
                        # the composite.
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayLights="flat",
                            shadows=False)

                        cmds.modelEditor(
                            model_panel, edit=True,
                            imagePlane=False, polymeshes=True,
                            nurbsSurfaces=True,
                            subdivSurfaces=True)

                        # Create solid Lambert
                        solid_lambert = cmds.shadingNode(
                            "lambert", asShader=True,
                            name="mme_solidColor_mtl")
                        checker_nodes.append(solid_lambert)
                        solid_sg = cmds.sets(
                            renderable=True,
                            noSurfaceShader=True,
                            empty=True,
                            name="mme_solidColor_SG")
                        checker_nodes.append(solid_sg)
                        cmds.connectAttr(
                            "{}.outColor".format(solid_lambert),
                            "{}.surfaceShader".format(solid_sg),
                            force=True)
                        chk_color = checker_color or (0.75, 0.75, 0.75)
                        cmds.setAttr(
                            "{}.color".format(solid_lambert),
                            chk_color[0], chk_color[1], chk_color[2],
                            type="double3")
                        cmds.setAttr(
                            "{}.transparency".format(solid_lambert),
                            0, 0, 0, type="double3")

                        if mm_transforms:
                            cmds.select(mm_transforms, replace=True)
                            cmds.hyperShade(assign=solid_lambert)
                            cmds.select(clear=True)

                        cmds.ogs(reset=True)
                        cmds.refresh(force=True)
                        cmds.playblast(
                            filename=composite_color_path,
                            format="image",
                            compression="png",
                            startTime=start_frame,
                            endTime=end_frame,
                            forceOverwrite=True,
                            sequenceTime=False,
                            clearCache=True,
                            viewer=False,
                            showOrnaments=False,
                            framePadding=4,
                            percent=100,
                            quality=100,
                            widthHeight=[1920, 1080],
                        )

                        # Restore shading before pass 3
                        for ms, sg in original_shading.items():
                            try:
                                if (cmds.objExists(ms)
                                        and cmds.objExists(sg)):
                                    cmds.sets(
                                        ms, edit=True,
                                        forceElement=sg)
                            except Exception:
                                pass
                        # Delete solid shader
                        for node in (solid_sg, solid_lambert):
                            try:
                                if cmds.objExists(node):
                                    cmds.delete(node)
                            except Exception:
                                pass
                        checker_nodes = [
                            n for n in checker_nodes
                            if n not in (solid_lambert, solid_sg)]

                        # --- Pass 3: B&W Checker Matte ---
                        self.log("Rendering matte pass...")
                        chk_lambert = cmds.shadingNode(
                            "lambert", asShader=True,
                            name="mme_matteCk_mtl")
                        checker_nodes.append(chk_lambert)
                        cmds.setAttr(
                            "{}.transparency".format(chk_lambert),
                            0, 0, 0, type="double3")

                        chk_sg = cmds.sets(
                            renderable=True,
                            noSurfaceShader=True,
                            empty=True,
                            name="mme_matteCk_SG")
                        checker_nodes.append(chk_sg)
                        cmds.connectAttr(
                            "{}.outColor".format(chk_lambert),
                            "{}.surfaceShader".format(chk_sg),
                            force=True)

                        chk_tex = cmds.shadingNode(
                            "checker", asTexture=True,
                            name="mme_matteCk_tex")
                        checker_nodes.append(chk_tex)
                        cmds.setAttr(
                            "{}.color1".format(chk_tex),
                            1, 1, 1, type="double3")
                        cmds.setAttr(
                            "{}.color2".format(chk_tex),
                            0, 0, 0, type="double3")

                        chk_place = cmds.shadingNode(
                            "place2dTexture", asUtility=True,
                            name="mme_matteCk_place")
                        checker_nodes.append(chk_place)
                        repeat = max(1, 33 - checker_scale)
                        cmds.setAttr(
                            "{}.repeatU".format(chk_place), repeat)
                        cmds.setAttr(
                            "{}.repeatV".format(chk_place), repeat)

                        for attr in (
                            "coverage", "translateFrame",
                            "rotateFrame",
                            "mirrorU", "mirrorV", "stagger",
                            "wrapU", "wrapV", "repeatUV",
                            "offset", "rotateUV", "noiseUV",
                            "vertexUvOne", "vertexUvTwo",
                            "vertexUvThree", "vertexCameraOne",
                        ):
                            if (cmds.attributeQuery(
                                    attr, node=chk_place,
                                    exists=True)
                                    and cmds.attributeQuery(
                                        attr, node=chk_tex,
                                        exists=True)):
                                cmds.connectAttr(
                                    "{}.{}".format(
                                        chk_place, attr),
                                    "{}.{}".format(
                                        chk_tex, attr),
                                    force=True)
                        cmds.connectAttr(
                            "{}.outUV".format(chk_place),
                            "{}.uvCoord".format(chk_tex),
                            force=True)
                        cmds.connectAttr(
                            "{}.outUvFilterSize".format(chk_place),
                            "{}.uvFilterSize".format(chk_tex),
                            force=True)
                        cmds.connectAttr(
                            "{}.outColor".format(chk_tex),
                            "{}.color".format(chk_lambert),
                            force=True)

                        if mm_transforms:
                            cmds.select(mm_transforms, replace=True)
                            cmds.hyperShade(assign=chk_lambert)
                            cmds.select(clear=True)

                        cmds.ogs(reset=True)
                        cmds.refresh(force=True)
                        cmds.playblast(
                            filename=composite_matte_path,
                            format="image",
                            compression="png",
                            startTime=start_frame,
                            endTime=end_frame,
                            forceOverwrite=True,
                            sequenceTime=False,
                            clearCache=True,
                            viewer=False,
                            showOrnaments=False,
                            framePadding=4,
                            percent=100,
                            quality=100,
                            widthHeight=[1920, 1080],
                        )

                        # Restore background
                        cmds.displayRGBColor(
                            "background", *original_bg)
                        cmds.displayRGBColor(
                            "backgroundTop", *original_bg_top)
                        cmds.displayRGBColor(
                            "backgroundBottom", *original_bg_bottom)
                        cmds.displayPref(
                            displayGradient=original_gradient)

                        # Restore polymesh visibility for cleanup
                        cmds.modelEditor(
                            model_panel, edit=True,
                            imagePlane=True, polymeshes=True,
                            nurbsSurfaces=True,
                            subdivSurfaces=True)

                        # Flag that composite renders are done;
                        # the playblast section below will composite
                        composite_rendered = True

                    else:
                        # --- Fallback: single-pass checker overlay ---
                        composite_rendered = False

                        chk_lambert = cmds.shadingNode(
                            "lambert", asShader=True,
                            name="mme_uvChecker_mtl")
                        checker_nodes.append(chk_lambert)
                        transp = 1.0 - (checker_opacity / 100.0)
                        cmds.setAttr(
                            "{}.transparency".format(chk_lambert),
                            transp, transp, transp, type="double3")

                        chk_sg = cmds.sets(
                            renderable=True,
                            noSurfaceShader=True,
                            empty=True,
                            name="mme_uvChecker_SG")
                        checker_nodes.append(chk_sg)
                        cmds.connectAttr(
                            "{}.outColor".format(chk_lambert),
                            "{}.surfaceShader".format(chk_sg),
                            force=True)

                        chk_color = checker_color or (0.75, 0.75, 0.75)
                        chk_color2 = (
                            chk_color[0] * 0.33,
                            chk_color[1] * 0.33,
                            chk_color[2] * 0.33,
                        )
                        chk_tex = cmds.shadingNode(
                            "checker", asTexture=True,
                            name="mme_uvChecker_tex")
                        checker_nodes.append(chk_tex)
                        cmds.setAttr(
                            "{}.color1".format(chk_tex),
                            chk_color[0], chk_color[1], chk_color[2],
                            type="double3")
                        cmds.setAttr(
                            "{}.color2".format(chk_tex),
                            chk_color2[0], chk_color2[1],
                            chk_color2[2],
                            type="double3")

                        chk_place = cmds.shadingNode(
                            "place2dTexture", asUtility=True,
                            name="mme_uvChecker_place")
                        checker_nodes.append(chk_place)
                        repeat = max(1, 33 - checker_scale)
                        cmds.setAttr(
                            "{}.repeatU".format(chk_place), repeat)
                        cmds.setAttr(
                            "{}.repeatV".format(chk_place), repeat)

                        for attr in (
                            "coverage", "translateFrame",
                            "rotateFrame",
                            "mirrorU", "mirrorV", "stagger",
                            "wrapU", "wrapV", "repeatUV",
                            "offset", "rotateUV", "noiseUV",
                            "vertexUvOne", "vertexUvTwo",
                            "vertexUvThree", "vertexCameraOne",
                        ):
                            if (cmds.attributeQuery(
                                    attr, node=chk_place,
                                    exists=True)
                                    and cmds.attributeQuery(
                                        attr, node=chk_tex,
                                        exists=True)):
                                cmds.connectAttr(
                                    "{}.{}".format(
                                        chk_place, attr),
                                    "{}.{}".format(
                                        chk_tex, attr),
                                    force=True)
                        cmds.connectAttr(
                            "{}.outUV".format(chk_place),
                            "{}.uvCoord".format(chk_tex),
                            force=True)
                        cmds.connectAttr(
                            "{}.outUvFilterSize".format(chk_place),
                            "{}.uvFilterSize".format(chk_tex),
                            force=True)
                        cmds.connectAttr(
                            "{}.outColor".format(chk_tex),
                            "{}.color".format(chk_lambert),
                            force=True)

                        if mm_transforms:
                            cmds.select(mm_transforms, replace=True)
                            cmds.hyperShade(assign=chk_lambert)
                            cmds.select(clear=True)

                        original_use_default_mtl = cmds.modelEditor(
                            model_panel, query=True,
                            useDefaultMaterial=True)
                        cmds.modelEditor(
                            model_panel, edit=True,
                            useDefaultMaterial=False)

                        original_display_textures = cmds.modelEditor(
                            model_panel, query=True,
                            displayTextures=True)
                        original_display_lights = cmds.modelEditor(
                            model_panel, query=True,
                            displayLights=True)
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayTextures=True,
                            displayLights="default")

                        cmds.ogs(reset=True)
                        cmds.currentTime(
                            cmds.currentTime(query=True))
                        cmds.refresh(force=True)

                except Exception as exc:
                    self._log_error("MM/FT Checker", exc)

            # --- Flat lighting (all playblast paths) ---
            original_flat_lighting = None
            if not raw_playblast and model_panel:
                try:
                    original_flat_lighting = cmds.modelEditor(
                        model_panel, query=True, displayLights=True)
                    cmds.modelEditor(
                        model_panel, edit=True, displayLights="flat")
                except Exception:
                    pass

            # --- Backface culling (all playblast paths) ---
            # Set to Full (3) on every mesh shape so back faces are
            # culled in wireframe, shaded, and textured views alike.
            original_culling = {}
            if not raw_playblast:
                for mesh in (cmds.ls(type="mesh", long=True) or []):
                    try:
                        original_culling[mesh] = cmds.getAttr(
                            mesh + ".backfaceCulling")
                        cmds.setAttr(mesh + ".backfaceCulling", 3)
                    except Exception:
                        pass

            try:
                # Ensure the model panel we configured is the active
                # viewport — playblast renders from the focused panel.
                if model_panel:
                    cmds.setFocus(model_panel)

                # Set colour management for the playblast.
                # Ensure the playblast output transform is Raw (sRGB).
                # This change persists in the scene file (not undone).
                if render_raw_srgb:
                    self._ensure_playblast_raw_srgb()

                cmds.refresh(force=True)

                if composite_rendered:
                    # Multi-pass composite: 3 passes already rendered,
                    # now composite them via ffmpeg.
                    plate_dir = os.path.dirname(
                        composite_plate_path)
                    plate_base = os.path.basename(
                        composite_plate_path)
                    color_dir = os.path.dirname(
                        composite_color_path)
                    color_base = os.path.basename(
                        composite_color_path)
                    matte_dir = os.path.dirname(
                        composite_matte_path)
                    matte_base = os.path.basename(
                        composite_matte_path)
                    opacity_01 = checker_opacity / 100.0

                    if png_mode:
                        # Composite to PNG sequence
                        out_dir = os.path.dirname(file_path)
                        if not os.path.exists(out_dir):
                            os.makedirs(out_dir)
                        encode_ok = self._encode_composite(
                            plate_dir, plate_base,
                            color_dir, color_base,
                            matte_dir, matte_base,
                            start_frame, out_dir,
                            opacity=opacity_01,
                            png_output=True)
                    elif mp4_mode:
                        encode_ok = self._encode_composite(
                            plate_dir, plate_base,
                            color_dir, color_base,
                            matte_dir, matte_base,
                            start_frame, mp4_output,
                            opacity=opacity_01)
                    else:
                        # Composite output — use .mp4 on macOS for
                        # reliable ffmpeg encoding; .mov on Windows.
                        composite_out = file_path
                        if sys.platform == "darwin":
                            composite_out = os.path.splitext(
                                file_path)[0] + ".mp4"
                        encode_ok = self._encode_composite(
                            plate_dir, plate_base,
                            color_dir, color_base,
                            matte_dir, matte_base,
                            start_frame, composite_out,
                            opacity=opacity_01)

                    if encode_ok:
                        # Cleanup composite temp dirs
                        if composite_tmp_dir:
                            self._cleanup_temp_pngs(
                                composite_tmp_dir)
                        # Also remove the mp4 temp dir if it was
                        # created empty by the caller
                        if mp4_mode and mp4_output:
                            mp4_tmp = os.path.dirname(file_path)
                            self._cleanup_temp_pngs(mp4_tmp)
                    else:
                        self.log(
                            "Composite failed — temp PNGs kept.")
                    return encode_ok
                elif mp4_mode:
                    # H.264 MP4 via ffmpeg: playblast temp PNGs, encode
                    png_dir = os.path.dirname(file_path)
                    if not os.path.exists(png_dir):
                        os.makedirs(png_dir)
                    self.log("Rendering...")
                    cmds.playblast(
                        filename=file_path,
                        format="image",
                        compression="png",
                        startTime=start_frame,
                        endTime=end_frame,
                        forceOverwrite=True,
                        sequenceTime=False,
                        clearCache=True,
                        viewer=False,
                        showOrnaments=show_hud,
                        framePadding=4,
                        percent=100,
                        quality=100,
                        widthHeight=[1920, 1080],
                    )
                    png_base = os.path.basename(file_path)
                    encode_ok = self._encode_mp4(
                        png_dir, png_base, start_frame, mp4_output)
                    if encode_ok:
                        self._cleanup_temp_pngs(png_dir)
                    else:
                        self.log(
                            "MP4 failed — temp PNGs kept.")
                    return encode_ok
                elif png_mode:
                    # PNG image sequence
                    png_dir = os.path.dirname(file_path)
                    if not os.path.exists(png_dir):
                        os.makedirs(png_dir)
                    self.log("Rendering...")
                    cmds.playblast(
                        filename=file_path,
                        format="image",
                        compression="png",
                        startTime=start_frame,
                        endTime=end_frame,
                        forceOverwrite=True,
                        sequenceTime=False,
                        clearCache=True,
                        viewer=False,
                        showOrnaments=show_hud,
                        framePadding=4,
                        percent=100,
                        quality=100,
                        widthHeight=[1920, 1080],
                    )
                else:
                    # H.264 .mov — strip extension, playblast appends it
                    self.log("Rendering...")
                    path_no_ext = file_path
                    if path_no_ext.lower().endswith(".mov"):
                        path_no_ext = path_no_ext[:-4]
                    cmds.playblast(
                        filename=path_no_ext,
                        format=pb_format,
                        compression="H.264",
                        startTime=start_frame,
                        endTime=end_frame,
                        forceOverwrite=True,
                        sequenceTime=False,
                        clearCache=True,
                        viewer=False,
                        showOrnaments=show_hud,
                        framePadding=4,
                        percent=100,
                        quality=70,
                        widthHeight=[1920, 1080],
                    )
                return True
            finally:
                # --- Restore Camera Track overrides ---
                for flag, val in original_editor_vis.items():
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True, **{flag: val})
                    except Exception:
                        pass
                if original_aa is not None:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals.multiSampleEnable",
                            original_aa)
                    except Exception:
                        pass
                if original_msaa_count is not None:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals.multiSampleCount",
                            original_msaa_count)
                    except Exception:
                        pass
                if original_smooth_wire is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            smoothWireframe=original_smooth_wire)
                    except Exception:
                        pass
                if original_display is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayAppearance=original_display)
                    except Exception:
                        pass
                if original_ct_wos is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            wireframeOnShaded=original_ct_wos)
                    except Exception:
                        pass
                # Restore useBackground shader assignments
                for mesh, sg in original_ct_shading.items():
                    try:
                        if cmds.objExists(mesh) and cmds.objExists(sg):
                            cmds.sets(mesh, edit=True,
                                      forceElement=sg)
                    except Exception:
                        pass
                for node in ct_bg_shader_nodes:
                    try:
                        if cmds.objExists(node):
                            cmds.delete(node)
                    except Exception:
                        pass

                # --- Restore Matchmove overrides ---
                # Restore shading before deleting checker nodes
                for mesh, sg in original_shading.items():
                    try:
                        if cmds.objExists(mesh) and cmds.objExists(sg):
                            cmds.sets(mesh, edit=True,
                                      forceElement=sg)
                    except Exception:
                        pass
                if original_display_textures is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayTextures=original_display_textures)
                    except Exception:
                        pass
                if original_display_lights is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayLights=original_display_lights)
                    except Exception:
                        pass
                if original_use_default_mtl is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            useDefaultMaterial=original_use_default_mtl)
                    except Exception:
                        pass
                if original_image_plane is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            imagePlane=original_image_plane)
                    except Exception:
                        pass
                if original_nurbs_curves is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            nurbsCurves=original_nurbs_curves)
                    except Exception:
                        pass
                for node in checker_nodes:
                    try:
                        if cmds.objExists(node):
                            cmds.delete(node)
                    except Exception:
                        pass
                # Restore display appearance
                if original_mm_display is not None and model_panel:
                    cmds.modelEditor(
                        model_panel, edit=True,
                        displayAppearance=original_mm_display)
                if original_mm_wos is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            wireframeOnShaded=original_mm_wos)
                    except Exception:
                        pass
                if original_mm_smooth_wire is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            smoothWireframe=original_mm_smooth_wire)
                    except Exception:
                        pass
                if original_mm_aa is not None:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals.multiSampleEnable",
                            original_mm_aa)
                    except Exception:
                        pass
                if original_mm_msaa_count is not None:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals.multiSampleCount",
                            original_mm_msaa_count)
                    except Exception:
                        pass
                if original_mm_motion_blur is not None:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals.motionBlurEnable",
                            original_mm_motion_blur)
                    except Exception:
                        pass
                # Restore isolate select
                if model_panel:
                    try:
                        cmds.isolateSelect(
                            model_panel,
                            state=original_isolate_state)
                    except Exception:
                        pass
                # Restore display layer visibility and playback
                for layer, val in original_layer_vis.items():
                    try:
                        if cmds.objExists(layer):
                            cmds.setAttr(
                                layer + ".visibility", val)
                    except Exception:
                        pass
                for layer, val in original_layer_playback.items():
                    try:
                        if cmds.objExists(layer):
                            cmds.setAttr(
                                layer + ".hideOnPlayback", val)
                    except Exception:
                        pass

                # --- Shared restores ---
                # Restore lighting mode
                if original_flat_lighting is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayLights=original_flat_lighting)
                    except Exception:
                        pass
                # Restore backface culling
                for mesh, val in original_culling.items():
                    try:
                        if cmds.objExists(mesh):
                            cmds.setAttr(mesh + ".backfaceCulling", val)
                    except Exception:
                        pass
                if (original_pan_zoom is not None
                        or original_far_clip is not None) and camera:
                    cam_shapes = cmds.listRelatives(
                        camera, shapes=True, type="camera") or []
                    if cam_shapes:
                        if original_pan_zoom is not None:
                            try:
                                cmds.setAttr(
                                    cam_shapes[0] + ".panZoomEnabled",
                                    original_pan_zoom)
                            except Exception:
                                pass
                        if original_far_clip is not None:
                            try:
                                cmds.setAttr(
                                    cam_shapes[0] + ".farClipPlane",
                                    original_far_clip)
                            except Exception:
                                pass
                if original_grid is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            grid=original_grid)
                    except Exception:
                        pass
                if original_cam and model_panel:
                    cmds.lookThru(model_panel, original_cam)
                if original_sel:
                    try:
                        cmds.select(original_sel, replace=True)
                    except Exception:
                        pass
                # --- HUD overlay cleanup ---
                for hud_name in hud_names_to_remove:
                    try:
                        if cmds.headsUpDisplay(hud_name, exists=True):
                            cmds.headsUpDisplay(hud_name, remove=True)
                    except Exception:
                        pass
                for hud_name, was_visible in original_hud_vis.items():
                    try:
                        if cmds.headsUpDisplay(hud_name, exists=True):
                            cmds.headsUpDisplay(
                                hud_name, edit=True,
                                visible=was_visible)
                    except Exception:
                        pass
                # Restore VP2.0 font settings
                if original_font_mode is not None:
                    try:
                        kwargs = {
                            "fontSettingMode": original_font_mode}
                        if original_font_size is not None:
                            kwargs["defaultFontSize"] = (
                                original_font_size)
                        cmds.displayPref(**kwargs)
                    except Exception:
                        pass
                # Playblast colour management is intentionally NOT
                # restored — the Raw (sRGB) setting persists in the
                # scene file per user preference.
        except Exception as e:
            self._log_error("Playblast", e)
            return False

    # --- Colour Management Helper ---

    def _ensure_playblast_raw_srgb(self):
        """Set the Prefs > Color Management > Playblast output
        transform to Raw (sRGB) if it isn't already.

        Uses ``outputTransformNames`` (the list accepted by the
        ``outputTransformName`` flag) so this works across synColor,
        ACES, and custom OCIO configs.  The change is left in the
        scene intentionally.
        """
        # --- Collect available output transforms ---
        output_transform_names = []
        try:
            output_transform_names = (
                cmds.colorManagementPrefs(
                    query=True, outputTransformNames=True) or [])
        except Exception as exc:
            sys.stderr.write(
                "[ExportGenie] outputTransformNames query "
                "failed: {}\n".format(exc))

        # --- Find a Raw candidate ---
        def _find_raw(names):
            """Return the first name that looks like a Raw / sRGB
            passthrough, or None."""
            for n in names:
                if n == "Raw":
                    return n
            for n in names:
                if n.startswith("Raw"):
                    return n
            for n in names:
                if "raw" in n.lower() and "srgb" in n.lower():
                    return n
            for n in names:
                if "raw" in n.lower():
                    return n
            return None

        chosen_name = _find_raw(output_transform_names)

        if not chosen_name:
            # Log viewNames too for diagnostics.
            view_names = []
            try:
                view_names = (
                    cmds.colorManagementPrefs(
                        query=True, viewNames=True) or [])
            except Exception:
                pass
            sys.stderr.write(
                "[ExportGenie] No Raw output transform found "
                "in OCIO config.\n")
            self.log(
                "Color management: Raw not found. "
                "See Script Editor.")
            return

        # --- Query what is currently set ---
        current_otn = None
        try:
            current_otn = cmds.colorManagementPrefs(
                query=True, outputTransformName=True,
                outputTarget="playblast")
        except Exception:
            pass

        if current_otn == chosen_name:
            return

        # --- Apply the setting ---
        # Per the Maya docs, outputTransformName implicitly handles
        # the transform mode (disables view-transform mode), so we
        # do NOT separately set outputUseViewTransform.
        self.log("Setting color management to Raw...")
        try:
            cmds.colorManagementPrefs(
                edit=True,
                outputTransformEnabled=True,
                outputTarget="playblast")
        except Exception as exc:
            sys.stderr.write(
                "[ExportGenie] outputTransformEnabled "
                "failed: {}\n".format(exc))
        try:
            cmds.colorManagementPrefs(
                edit=True,
                outputTransformName=chosen_name,
                outputTarget="playblast")
        except Exception as exc:
            sys.stderr.write(
                "[ExportGenie] outputTransformName "
                "failed: {}\n".format(exc))
        try:
            cmds.colorManagementPrefs(refresh=True)
        except Exception:
            pass

        # --- Verify it took effect ---
        verify_otn = None
        try:
            verify_otn = cmds.colorManagementPrefs(
                query=True, outputTransformName=True,
                outputTarget="playblast")
        except Exception:
            pass
        if verify_otn != chosen_name:
            sys.stderr.write(
                "[ExportGenie] Color management verification "
                "failed. Expected '{}', got '{}'.\n".format(
                    chosen_name, verify_otn))

    # --- JSX Helper Methods ---

    @staticmethod
    def _get_fps():
        """Map Maya's current time unit to FPS float."""
        unit = cmds.currentUnit(query=True, time=True)
        fps_map = {
            "game": 15.0,
            "film": 24.0,
            "pal": 25.0,
            "ntsc": 30.0,
            "show": 48.0,
            "palf": 50.0,
            "ntscf": 60.0,
            "23.976fps": 23.976,
            "29.97fps": 29.97,
            "29.97df": 29.97,
            "47.952fps": 47.952,
            "59.94fps": 59.94,
            "44100fps": 44100.0,
            "48000fps": 48000.0,
        }
        return fps_map.get(unit, 24.0)

    @staticmethod
    def _sanitize_jsx_var(name):
        """Clean a name for use as a JavaScript variable name."""
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        if sanitized and sanitized[0].isdigit():
            sanitized = "obj_" + sanitized
        return sanitized or "unnamed"

    @staticmethod
    def _escape_jsx_string(name):
        """Escape a name for use in a JavaScript string literal."""
        return name.replace("\\", "\\\\").replace("'", "\\'")

    @staticmethod
    def _jsx_header(scene_name):
        """Generate JSX file header lines."""
        lines = []
        lines.append("// Auto-generated JSX from Export Genie v{}".format(
            TOOL_VERSION))
        lines.append("// Scene: {}".format(scene_name))
        lines.append("// Coordinate system: Maya Y-up converted to AE")
        lines.append("")
        lines.append("app.activate();")
        lines.append("")
        return lines

    @staticmethod
    def _jsx_helpers():
        """Generate JSX helper functions."""
        lines = []
        lines.append("function findComp(nm) {")
        lines.append("    var i, n, prjitm;")
        lines.append("")
        lines.append("    prjitm = app.project.items;")
        lines.append("    n = prjitm.length;")
        lines.append("    for (i = 1; i <= n; i++) {")
        lines.append("        if (prjitm[i].name == nm)")
        lines.append("            return prjitm[i];")
        lines.append("    }")
        lines.append("    return null;")
        lines.append("}")
        lines.append("")
        lines.append("function firstComp() {")
        lines.append("    var i, n, prjitm;")
        lines.append("")
        lines.append("    if (app.project.activeItem.typeName == \"Composition\")")
        lines.append("        return app.project.activeItem;")
        lines.append("")
        lines.append("    prjitm = app.project.items;")
        lines.append("    n = prjitm.length;")
        lines.append("    for (i = 1; i <= n; i++) {")
        lines.append("        if (prjitm[i].typeName == \"Composition\")")
        lines.append("            return prjitm[i];")
        lines.append("    }")
        lines.append("    return null;")
        lines.append("}")
        lines.append("")
        lines.append("function deselectAll(items) {")
        lines.append("    var i, itm;")
        lines.append("")
        lines.append("    for (i = 1; i <= items.length; i++) {")
        lines.append("        itm = items[i];")
        lines.append("        if (itm instanceof FolderItem)")
        lines.append("            deselectAll(itm.items);")
        lines.append("        itm.selected = false;")
        lines.append("    };")
        lines.append("}")
        lines.append("")
        return lines

    @staticmethod
    def _jsx_footer():
        """Generate JSX file footer lines."""
        lines = []
        lines.append("// Open comp in viewer")
        lines.append("comp.selected = true;")
        lines.append("deselectAll(app.project.items);")
        lines.append("comp.selected = true;")
        lines.append("comp.openInViewer();")
        lines.append("")
        lines.append("app.endUndoGroup();")
        lines.append("alert('Scene import complete!');")
        lines.append("")
        lines.append("} // End SceneImportFunction")
        lines.append("")
        lines.append("SceneImportFunction();")
        return lines

    # --- JSX Coordinate Conversion ---

    @staticmethod
    def _compute_ae_scale(camera):
        """Compute the Maya-to-AE-pixel scale.

        SynthEyes uses rescale = 10, calibrated for its internal inch-based
        unit system. We convert from whatever Maya's linear unit is to
        match that convention.
        """
        unit = cmds.currentUnit(query=True, linear=True)
        cm_per_unit = {
            'mm': 0.1, 'cm': 1.0, 'in': 2.54,
            'ft': 30.48, 'yd': 91.44, 'm': 100.0,
        }
        cmu = cm_per_unit.get(unit, 1.0)
        return 10.0 * cmu / 2.54

    @staticmethod
    def _get_image_plane_path(camera):
        """Return the file path from the camera's image plane, or None.

        Silently returns None if there is no image plane, no file path,
        or any error occurs.
        """
        try:
            cam_shapes = cmds.listRelatives(
                camera, shapes=True, type="camera") or []
            if not cam_shapes:
                return None
            img_planes = cmds.listConnections(
                cam_shapes[0] + ".imagePlane", type="imagePlane") or []
            if not img_planes:
                return None
            path = cmds.getAttr(img_planes[0] + ".imageName")
            if path and path.strip():
                return path.strip()
            return None
        except Exception:
            return None

    @staticmethod
    def _get_image_plane_transforms(camera):
        """Return transform nodes for image planes connected to *camera*.

        Returns an empty list on failure or if no image planes exist.
        """
        try:
            cam_shapes = cmds.listRelatives(
                camera, shapes=True, type="camera") or []
            if not cam_shapes:
                return []
            img_planes = cmds.listConnections(
                cam_shapes[0] + ".imagePlane", type="imagePlane") or []
            transforms = []
            for ip in img_planes:
                parents = cmds.listRelatives(ip, parent=True) or []
                if parents:
                    transforms.append(parents[0])
            return transforms
        except Exception:
            return []

    @staticmethod
    def _world_matrix_to_ae(node, ae_scale, comp_cx, comp_cy):
        """Convert a Maya node's world-space transform to AE position + rotation.

        Position comes from the world matrix (correct absolute placement).
        Rotation comes from the *local* (object-space) matrix so that any
        parent-group orientation (e.g. a SynthEyes tracking group that
        converts Z-up to Y-up) is excluded — matching the behaviour of
        direct SynthEyes-to-AE exports.
        World-space scale is also returned (from the world matrix) so
        callers can account for parent scale.

        Returns:
            tuple: ((x, y, z), (rx_deg, ry_deg, rz_deg), (sx, sy, sz))
        """
        m = cmds.xform(node, query=True, worldSpace=True, matrix=True)

        # Position from world matrix translation (row 3, Maya row-major)
        tx = m[12]
        ty = m[13]
        tz = m[14]
        x_ae = tx * ae_scale + comp_cx
        y_ae = -ty * ae_scale + comp_cy
        z_ae = -tz * ae_scale

        # World-space scale from world matrix column magnitudes
        sx = math.sqrt(m[0] ** 2 + m[1] ** 2 + m[2] ** 2)
        sy = math.sqrt(m[4] ** 2 + m[5] ** 2 + m[6] ** 2)
        sz = math.sqrt(m[8] ** 2 + m[9] ** 2 + m[10] ** 2)

        # --- Rotation from LOCAL matrix (excludes parent group rotation) ---
        ml = cmds.xform(node, query=True, objectSpace=True, matrix=True)

        lsx = math.sqrt(ml[0] ** 2 + ml[1] ** 2 + ml[2] ** 2)
        lsy = math.sqrt(ml[4] ** 2 + ml[5] ** 2 + ml[6] ** 2)
        lsz = math.sqrt(ml[8] ** 2 + ml[9] ** 2 + ml[10] ** 2)
        if lsx < 1e-9:
            lsx = 1.0
        if lsy < 1e-9:
            lsy = 1.0
        if lsz < 1e-9:
            lsz = 1.0

        # Normalized local rotation matrix rows
        r00 = ml[0] / lsx;  r01 = ml[1] / lsx;  r02 = ml[2] / lsx
        r10 = ml[4] / lsy;  r11 = ml[5] / lsy;  r12 = ml[6] / lsy
        r20 = ml[8] / lsz;  r21 = ml[9] / lsz;  r22 = ml[10] / lsz

        # Apply coordinate transform T * R * T  (T = diag(1, -1, -1))
        # TRT_row = [[r00, -r01, -r02], [-r10, r11, r12], [-r20, r21, r22]]
        # R_ae_col = transpose(TRT_row):
        #   [[r00, -r10, -r20], [-r01, r11, r21], [-r02, r12, r22]]
        #
        # AE applies rotation as Rx * Ry * Rz (intrinsic XYZ).
        # Decompose R_ae_col as Rx(a)*Ry(b)*Rz(g):
        #   R[0][2] = sin(b)  = -r20  -> b = asin(-r20)
        #   R[1][2] = -sa*cb  =  r21  -> a = atan2(-r21, r22)
        #   R[0][1] = -cb*sg  = -r10  -> g = atan2( r10, r00)
        ry_ae = math.asin(max(-1.0, min(1.0, -r20)))
        cos_ry = math.cos(ry_ae)
        if abs(cos_ry) > 1e-6:
            rx_ae = math.atan2(-r21, r22)
            rz_ae = math.atan2(r10, r00)
        else:
            rx_ae = 0.0
            rz_ae = math.atan2(-r01, r11)

        rx_deg = math.degrees(rx_ae)
        ry_deg = math.degrees(ry_ae)
        rz_deg = math.degrees(rz_ae)

        return (x_ae, y_ae, z_ae), (rx_deg, ry_deg, rz_deg), (sx, sy, sz)

    # --- JSX Camera ---

    def _jsx_camera(self, camera, start_frame, end_frame, fps,
                    comp_width, comp_height, ae_scale):
        """Generate JSX lines for a camera with per-frame keyframes."""
        jsx = []
        shapes = cmds.listRelatives(camera, shapes=True, type="camera") or []
        if not shapes:
            self.log("JSX failed — camera has no shape node.")
            return jsx
        cam_shape = shapes[0]

        focal_length = cmds.getAttr(cam_shape + ".focalLength")
        h_aperture_inches = cmds.getAttr(cam_shape + ".horizontalFilmAperture")
        h_aperture_mm = h_aperture_inches * 25.4
        ae_zoom = focal_length * comp_width / h_aperture_mm

        layer_var = "camera_{}".format(self._sanitize_jsx_var(camera))
        layer_name = self._escape_jsx_string(camera)

        comp_cx = comp_width / 2.0
        comp_cy = comp_height / 2.0

        jsx.append("var {var} = comp.layers.addCamera('{name}', [0, 0]);".format(
            var=layer_var, name=layer_name))
        jsx.append("{}.autoOrient = AutoOrientType.NO_AUTO_ORIENT;".format(layer_var))
        jsx.append("")
        jsx.append("var timesArray = new Array();")
        jsx.append("var posArray = new Array();")
        jsx.append("var rotXArray = new Array();")
        jsx.append("var rotYArray = new Array();")
        jsx.append("var rotZArray = new Array();")

        for frame in range(int(start_frame), int(end_frame) + 1):
            cmds.currentTime(frame)
            pos, rot, _ = self._world_matrix_to_ae(
                camera, ae_scale, comp_cx, comp_cy
            )

            time_sec = (frame - start_frame + 1) / fps

            jsx.append("timesArray.push({:.10f});".format(time_sec))
            jsx.append("posArray.push([{:.10f}, {:.10f}, {:.10f}]);".format(
                pos[0], pos[1], pos[2]))
            jsx.append("rotXArray.push({:.10f});".format(rot[0]))
            jsx.append("rotYArray.push({:.10f});".format(rot[1]))
            jsx.append("rotZArray.push({:.10f});".format(rot[2]))

        jsx.append("")
        jsx.append("{v}.position.setValuesAtTimes(timesArray, posArray);".format(v=layer_var))
        jsx.append("{v}.rotationX.setValuesAtTimes(timesArray, rotXArray);".format(v=layer_var))
        jsx.append("{v}.rotationY.setValuesAtTimes(timesArray, rotYArray);".format(v=layer_var))
        jsx.append("{v}.rotationZ.setValuesAtTimes(timesArray, rotZArray);".format(v=layer_var))
        jsx.append("{v}.zoom.setValue({z:.10f});".format(v=layer_var, z=ae_zoom))
        jsx.append("")
        return jsx

    # --- JSX Source Footage ---

    @staticmethod
    def _jsx_footage(image_path, fps, duration, comp_width, comp_height):
        """Generate JSX lines to import source footage as background layer.

        The footage is imported as a sequence and added to the comp.
        If the file doesn't exist on the AE machine, a placeholder is
        created instead.  The layer is moved to the bottom of the stack.

        image_path may be relative (to the JSX file) or absolute (if on
        a different drive).  Relative paths are resolved against the
        running script's parent folder via ``$.fileName``.
        """
        jsx = []
        # Normalise path separators for JSX (forward slashes)
        jsx_path = image_path.replace("\\", "/")

        jsx.append("// Source footage")
        # Resolve relative paths against the JSX file's directory
        if not os.path.isabs(image_path):
            jsx.append("var _scriptDir = (new File($.fileName)).parent;")
            jsx.append(
                "var footageFile = new File("
                "_scriptDir.fsName + '/' + '{}');".format(jsx_path))
        else:
            jsx.append("var footageFile = File('{}');".format(jsx_path))
        jsx.append("var srcFootage;")
        jsx.append("if (!footageFile.exists) {")
        jsx.append("    srcFootage = app.project.importPlaceholder("
                   "'SourcePH', {w}, {h}, {fps}, {dur});".format(
                       w=comp_width, h=comp_height, fps=fps, dur=duration))
        jsx.append("} else {")
        jsx.append("    var footageOpts = new ImportOptions();")
        jsx.append("    footageOpts.file = footageFile;")
        jsx.append("    footageOpts.sequence = true;")
        jsx.append("    footageOpts.importAs = ImportAsType.FOOTAGE;")
        jsx.append("    srcFootage = app.project.importFile(footageOpts);")
        jsx.append("};")
        jsx.append("srcFootage.pixelAspect = 1;")
        jsx.append("srcFootage.mainSource.conformFrameRate = {};".format(fps))
        jsx.append("var bkgLayer = comp.layers.add(srcFootage, {});".format(
            duration))
        jsx.append("srcFootage.selected = false;")
        jsx.append("bkgLayer.startTime = {};".format(1.0 / fps))
        jsx.append("bkgLayer.moveToEnd();")
        jsx.append("")
        return jsx

    # --- JSX Solid from Plane ---

    def _jsx_solid_from_plane(self, geo_child, start_frame, end_frame,
                              fps, comp_width, comp_height, ae_scale):
        """Generate JSX that creates an AE solid to represent a Maya plane.

        A simple quad in Maya becomes a 3-D solid in AE (matching the
        SynthEyes direct-export behaviour).  The solid is created at comp
        dimensions, rotated rx=-90 to lie on the ground plane, and scaled
        to match the Maya plane's world-space extent.
        """
        jsx = []
        short_name = geo_child.rsplit("|", 1)[-1]
        layer_var = "solid_{}".format(self._sanitize_jsx_var(short_name))
        layer_name = self._escape_jsx_string(short_name)
        comp_cx = comp_width / 2.0
        comp_cy = comp_height / 2.0

        # Plane world-space bounding box → dimensions
        bbox = cmds.exactWorldBoundingBox(geo_child)
        plane_w = abs(bbox[3] - bbox[0])  # X extent
        plane_d = abs(bbox[5] - bbox[2])  # Z extent

        # Solid scale: map comp-sized solid to Maya-plane AE dimensions
        ae_w = plane_w * ae_scale
        ae_d = plane_d * ae_scale
        scale_x = ae_w / comp_width * 100.0
        scale_y = ae_d / comp_height * 100.0
        scale_z = 100.0

        jsx.append(
            "var {v} = comp.layers.addSolid("
            "[0.5, 0.5, 0.5], '{nm}', {w}, {h}, 1.0, comp.duration);".format(
                v=layer_var, nm=layer_name, w=comp_width, h=comp_height))
        jsx.append("{v}.threeDLayer = true;".format(v=layer_var))
        jsx.append("")

        pos, rot, _ = self._world_matrix_to_ae(
            geo_child, ae_scale, comp_cx, comp_cy
        )
        # Solid starts in XY; rx=-90 puts it on the ground (XZ).
        # Compose with any local rotation the plane may have.
        rx_final = rot[0] - 90.0

        jsx.append("{v}.position.setValue([{x:.10f}, {y:.10f}, {z:.10f}]);".format(
            v=layer_var, x=pos[0], y=pos[1], z=pos[2]))
        jsx.append("{v}.rotationX.setValue({:.10f});".format(rx_final, v=layer_var))
        jsx.append("{v}.rotationY.setValue({:.10f});".format(rot[1], v=layer_var))
        jsx.append("{v}.rotationZ.setValue({:.10f});".format(rot[2], v=layer_var))
        jsx.append("{v}.scale.setValue([{:.10f}, {:.10f}, {:.10f}]);".format(
            scale_x, scale_y, scale_z, v=layer_var))
        jsx.append("")
        return jsx

    # --- JSX Mesh from Geo (OBJ Import) ---

    def _jsx_mesh_from_geo(self, geo_child, obj_filename, start_frame,
                           end_frame, fps, comp_width, comp_height, ae_scale):
        """Generate JSX lines that import an OBJ file into the AE comp.

        Uses ImportOptions + importFile() + layers.add() so the actual
        3-D geometry is visible in After Effects, rather than a bare null.
        """
        jsx = []
        short_name = geo_child.rsplit("|", 1)[-1]
        layer_var = "mesh_{}".format(self._sanitize_jsx_var(short_name))
        footage_var = "objFootage_{}".format(
            self._sanitize_jsx_var(short_name))
        layer_name = self._escape_jsx_string(short_name)
        obj_fn_escaped = self._escape_jsx_string(obj_filename)

        comp_cx = comp_width / 2.0
        comp_cy = comp_height / 2.0

        # AE maps 1 OBJ unit = 512 pixels at 100 % scale.
        scale_factor = ae_scale * 100.0 / 512.0

        # Import the OBJ file from the same directory as the JSX script.
        jsx.append("var importOptions = new ImportOptions();")
        jsx.append(
            "importOptions.file = File("
            "new File($.fileName).parent.fsName + '/{fn}');".format(
                fn=obj_fn_escaped))
        jsx.append(
            "var {fv} = app.project.importFile(importOptions);".format(
                fv=footage_var))
        jsx.append("{fv}.selected = false;".format(fv=footage_var))
        jsx.append("app.beginSuppressDialogs();")
        jsx.append(
            "var {lv} = comp.layers.add({fv}, comp.duration);".format(
                lv=layer_var, fv=footage_var))
        jsx.append("{lv}.name = '{nm}';".format(
            lv=layer_var, nm=layer_name))
        jsx.append("app.endSuppressDialogs(true);")
        jsx.append("")

        is_animated = bool(
            cmds.listConnections(geo_child, type="animCurve")
        )

        if is_animated:
            jsx.append("var timesArray = new Array();")
            jsx.append("var posArray = new Array();")
            jsx.append("var rotXArray = new Array();")
            jsx.append("var rotYArray = new Array();")
            jsx.append("var rotZArray = new Array();")
            jsx.append("var scaleArray = new Array();")

            for frame in range(int(start_frame), int(end_frame) + 1):
                cmds.currentTime(frame)
                pos, rot, ws = self._world_matrix_to_ae(
                    geo_child, ae_scale, comp_cx, comp_cy
                )
                sx = ws[0] * scale_factor
                sy = ws[1] * scale_factor
                sz = ws[2] * scale_factor

                time_sec = (frame - start_frame + 1) / fps

                jsx.append("timesArray.push({:.10f});".format(time_sec))
                jsx.append("posArray.push([{:.10f}, {:.10f}, {:.10f}]);".format(
                    pos[0], pos[1], pos[2]))
                jsx.append("rotXArray.push({:.10f});".format(rot[0]))
                jsx.append("rotYArray.push({:.10f});".format(rot[1]))
                jsx.append("rotZArray.push({:.10f});".format(rot[2]))
                jsx.append("scaleArray.push([{:.10f}, {:.10f}, {:.10f}]);".format(
                    sx, sy, sz))

            jsx.append("")
            jsx.append("{v}.position.setValuesAtTimes(timesArray, posArray);".format(v=layer_var))
            jsx.append("{v}.rotationX.setValuesAtTimes(timesArray, rotXArray);".format(v=layer_var))
            jsx.append("{v}.rotationY.setValuesAtTimes(timesArray, rotYArray);".format(v=layer_var))
            jsx.append("{v}.rotationZ.setValuesAtTimes(timesArray, rotZArray);".format(v=layer_var))
            jsx.append("{v}.scale.setValuesAtTimes(timesArray, scaleArray);".format(v=layer_var))
        else:
            pos, rot, ws = self._world_matrix_to_ae(
                geo_child, ae_scale, comp_cx, comp_cy
            )
            sx = ws[0] * scale_factor
            sy = ws[1] * scale_factor
            sz = ws[2] * scale_factor

            jsx.append("{v}.position.setValue([{:.10f}, {:.10f}, {:.10f}]);".format(
                pos[0], pos[1], pos[2], v=layer_var))
            jsx.append("{v}.rotationX.setValue({:.10f});".format(rot[0], v=layer_var))
            jsx.append("{v}.rotationY.setValue({:.10f});".format(rot[1], v=layer_var))
            jsx.append("{v}.rotationZ.setValue({:.10f});".format(rot[2], v=layer_var))
            jsx.append("{v}.scale.setValue([{:.10f}, {:.10f}, {:.10f}]);".format(
                sx, sy, sz, v=layer_var))

        jsx.append("")
        return jsx

    def _jsx_null_from_locator(self, locator_node, start_frame, end_frame,
                               fps, comp_width, comp_height, ae_scale):
        """Generate JSX for a Maya locator as a position-only 3D null in AE.

        Used for SynthEyes tracking markers — no OBJ, no rotation/scale.
        """
        jsx = []
        short_name = locator_node.rsplit("|", 1)[-1]
        layer_var = "loc_{}".format(self._sanitize_jsx_var(short_name))
        layer_name = self._escape_jsx_string(short_name)
        comp_cx = comp_width / 2.0
        comp_cy = comp_height / 2.0

        jsx.append("var {var} = comp.layers.addNull();".format(var=layer_var))
        jsx.append("{var}.name = '{name}';".format(
            var=layer_var, name=layer_name))
        jsx.append("{var}.threeDLayer = true;".format(var=layer_var))
        jsx.append(
            "{var}.property('Anchor Point')"
            ".setValue([0, 0, 0]);".format(var=layer_var)
        )
        jsx.append("")

        is_animated = bool(
            cmds.listConnections(locator_node, type="animCurve")
        )

        if is_animated:
            jsx.append("var timesArray = new Array();")
            jsx.append("var posArray = new Array();")

            for frame in range(int(start_frame), int(end_frame) + 1):
                cmds.currentTime(frame)
                pos, _, _ = self._world_matrix_to_ae(
                    locator_node, ae_scale, comp_cx, comp_cy
                )
                time_sec = (frame - start_frame + 1) / fps

                jsx.append("timesArray.push({:.10f});".format(time_sec))
                jsx.append(
                    "posArray.push([{:.10f}, {:.10f}, {:.10f}]);".format(
                        pos[0], pos[1], pos[2]
                    )
                )

            jsx.append("")
            jsx.append(
                "{v}.position"
                ".setValuesAtTimes(timesArray, posArray);".format(
                    v=layer_var)
            )
        else:
            pos, _, _ = self._world_matrix_to_ae(
                locator_node, ae_scale, comp_cx, comp_cy
            )
            jsx.append(
                "{v}.position"
                ".setValue([{x:.10f}, {y:.10f}, {z:.10f}]);".format(
                    v=layer_var, x=pos[0], y=pos[1], z=pos[2])
            )
        jsx.append("")
        return jsx

    # --- JSX Orchestrator ---

    def export_jsx(self, jsx_path, obj_paths, camera, geo_root,
                   start_frame, end_frame):
        """Export After Effects JSX + OBJ files.

        Args:
            jsx_path: Output .jsx file path.
            obj_paths: dict of {geo_child_name: obj_file_path}.
            camera: Maya camera transform (or None).
            geo_root: Maya geo root transform (or None).
            start_frame: First frame.
            end_frame: Last frame.

        Returns:
            bool: True on success.
        """
        try:
            fps = self._get_fps()
            comp_width = cmds.getAttr("defaultResolution.width")
            comp_height = cmds.getAttr("defaultResolution.height")
            duration = (end_frame - start_frame + 1) / fps
            ae_scale = self._compute_ae_scale(camera) if camera else 1.0

            scene_short = cmds.file(
                query=True, sceneName=True, shortName=True
            )
            scene_base = VersionParser.get_scene_base_name(scene_short)

            jsx_lines = []

            # Header
            jsx_lines.extend(self._jsx_header(scene_base))

            # Helpers
            jsx_lines.extend(self._jsx_helpers())

            # Main function
            jsx_lines.append("function SceneImportFunction() {")
            jsx_lines.append("")
            jsx_lines.append("app.exitAfterLaunchAndEval = false;")
            jsx_lines.append("")
            jsx_lines.append("app.beginUndoGroup('Scene Import');")
            jsx_lines.append("")

            # Create composition
            jsx_lines.append(
                "var comp = app.project.items.addComp('{name}', {w}, {h}, 1.0, {dur}, {fps});".format(
                    name=scene_base, w=comp_width, h=comp_height,
                    dur=duration, fps=fps
                )
            )
            jsx_lines.append("comp.displayStartFrame = 1;")
            jsx_lines.append("")

            # Camera
            if camera:
                cam_jsx = self._jsx_camera(
                    camera, start_frame, end_frame, fps,
                    comp_width, comp_height, ae_scale
                )
                jsx_lines.extend(cam_jsx)

            # Export OBJs and generate null layers
            if geo_root:
                children = cmds.listRelatives(
                    geo_root, children=True, type="transform",
                    fullPath=True,
                ) or []
                if not children:
                    # geo_root itself is the only geo
                    gr_long = cmds.ls(geo_root, long=True)
                    children = gr_long if gr_long else [geo_root]
                # Skip camera (and its parent groups) from geo children
                if camera:
                    children = [
                        c for c in children
                        if not self._is_descendant_of(camera, c)
                    ]
                for child in children:
                    # Use short name for display/keys, long path
                    # for Maya commands to avoid ambiguity
                    child_short = child.rsplit("|", 1)[-1]
                    child_lower = child_short.lower()

                    # Skip chisels groups entirely
                    if "chisels" in child_lower:
                        continue

                    # Nulls groups: each locator becomes a position-only null
                    if "nulls" in child_lower:
                        locator_transforms = cmds.listRelatives(
                            child, children=True, type="transform"
                        ) or []
                        for loc_tfm in locator_transforms:
                            shapes = (
                                cmds.listRelatives(
                                    loc_tfm, shapes=True, type="locator"
                                ) or []
                            )
                            if not shapes:
                                continue
                            loc_jsx = self._jsx_null_from_locator(
                                loc_tfm, start_frame, end_frame,
                                fps, comp_width, comp_height, ae_scale
                            )
                            jsx_lines.extend(loc_jsx)
                        continue

                    # Simple planes → AE solid (no OBJ needed)
                    if self._is_simple_plane(child):
                        geo_jsx = self._jsx_solid_from_plane(
                            child, start_frame, end_frame,
                            fps, comp_width, comp_height, ae_scale
                        )
                        jsx_lines.extend(geo_jsx)
                        continue

                    # Regular geo: OBJ import (skip if no mesh)
                    if child not in obj_paths:
                        continue
                    meshes = cmds.listRelatives(
                        child, allDescendents=True,
                        type="mesh", fullPath=True) or []
                    if not meshes:
                        continue
                    obj_path = obj_paths[child]
                    obj_filename = os.path.basename(obj_path)

                    self.export_obj(obj_path, child)

                    geo_jsx = self._jsx_mesh_from_geo(
                        child, obj_filename, start_frame, end_frame,
                        fps, comp_width, comp_height, ae_scale
                    )
                    jsx_lines.extend(geo_jsx)

            # Source footage (from camera image plane, added last = bottom layer)
            if camera:
                img_path = self._get_image_plane_path(camera)
                if img_path:
                    # Make path relative to JSX file location when possible
                    try:
                        jsx_dir = os.path.dirname(os.path.abspath(jsx_path))
                        rel_path = os.path.relpath(img_path, jsx_dir)
                        footage_path = rel_path
                    except ValueError:
                        # Different drives on Windows — keep absolute
                        footage_path = img_path
                    jsx_lines.extend(self._jsx_footage(
                        footage_path, fps, duration,
                        comp_width, comp_height))

            # Footer
            jsx_lines.extend(self._jsx_footer())

            # Write JSX file
            with open(jsx_path, "w") as f:
                f.write("\n".join(jsx_lines))

            return True
        except Exception as e:
            self._log_error("JSX", e)
            return False


# ---------------------------------------------------------------------------
# MultiExportUI
# ---------------------------------------------------------------------------
class MultiExportUI(object):
    """Main UI window built with maya.cmds — two-tab layout."""

    def __init__(self):
        self.window = None
        self.tab_layout = None
        # Shared
        self.scene_info_text = None
        self.version_text = None
        self.export_root_field = None
        self.version_field = None
        self.start_frame_field = None
        self.end_frame_field = None
        self.tpose_checkbox = None
        self.tpose_frame_field = None
        self.log_field = None
        self.progress_bar = None
        self.progress_label = None
        # Camera Track tab (ct_)
        self.ct_camera_field = None
        self.ct_geo_fields = []
        self.ct_geo_container = None
        self.ct_geo_btn_row = None
        self.ct_ma_checkbox = None
        self.ct_jsx_checkbox = None
        self.ct_fbx_checkbox = None
        self.ct_abc_checkbox = None
        self.ct_mov_checkbox = None
        self.ct_mov_format_menu = None
        # Playblast settings (consolidated in Playblast Settings tab)
        self.pb_context_menu = None
        self.pb_raw_playblast_cb = None
        self.pb_custom_vt_cb = None
        self.pb_wireframe_shader_cb = None
        self.pb_aa16_cb = None
        self.pb_hud_overlay_cb = None
        self.pb_far_clip = None
        self.pb_checker_color = None
        self.pb_checker_scale = None
        self.pb_checker_opacity = None
        # Matchmove tab (mm_)
        self.mm_camera_field = None
        self.mm_static_geo_fields = []
        self.mm_static_geo_container = None
        self.mm_static_geo_btn_row = None
        self.mm_rig_geo_pairs = []        # [{"rig_field", "geo_field", "row"}]
        self.mm_rig_geo_container = None  # columnLayout for dynamic pairs
        self.mm_btn_row = None            # +/- button row (rebuilt dynamically)
        self.mm_add_btn = None
        self.mm_minus_btn = None
        self.mm_ma_checkbox = None
        self.mm_fbx_checkbox = None
        self.mm_abc_checkbox = None
        self.mm_mov_checkbox = None
        self.mm_mov_format_menu = None
        # Preview mode state
        self._preview_active = False
        self._preview_state = {}
        self._preview_buttons = []
        self._preview_hints = []

    def show(self):
        """Launch the Export Genie UI via workspaceControl."""
        launch()

    def _build_ui_contents(self):
        """Build all UI contents inside the workspaceControl."""
        self.window = WORKSPACE_CONTROL_NAME

        cmds.scrollLayout(
            childResizable=True,
            verticalScrollBarThickness=16,
            horizontalScrollBarThickness=0,
        )

        cmds.columnLayout(
            adjustableColumn=True, rowSpacing=4, columnAttach=("both", 6)
        )

        cmds.separator(height=4, style="none")

        # --- Support contact ---
        support_row = cmds.rowLayout(
            numberOfColumns=2, adjustableColumn=2,
            columnWidth2=(200, 220),
            columnAlign2=("left", "left"))
        cmds.text(
            label="For support or issues, please contact ")
        cmds.iconTextButton(
            style="textOnly",
            label="Shannon Gold",
            font="boldLabelFont",
            command=lambda *_: __import__("webbrowser").open(
                "mailto:sgold1@pdoexperts.fb.com"
                "?subject=Export Genie {}".format(TOOL_VERSION)),
            annotation="sgold1@pdoexperts.fb.com",
        )
        cmds.setParent("..")

        # --- Shared: Scene Info ---
        self._build_scene_info()

        # --- Shared: Export Root ---
        self._build_export_root()

        # --- Tab Layout ---
        self.tab_layout = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

        # Tab 1: Camera Track Export
        ct_tab = self._build_camera_track_tab()

        # Tab 2: Matchmove Export
        mm_tab = self._build_matchmove_tab()

        # Tab 3: Face Track Export
        ft_tab = self._build_face_track_tab()

        # Tab 4: Playblast Settings
        pb_tab = self._build_playblast_tab()

        cmds.tabLayout(
            self.tab_layout,
            edit=True,
            tabLabel=(
                (ct_tab, "Camera Track"),
                (mm_tab, "Matchmove"),
                (ft_tab, "Face Track"),
                (pb_tab, "Playblast Settings"),
            ),
        )
        cmds.setParent("..")

        # --- Shared: Frame Range ---
        self._build_frame_range()

        # --- Export Button ---
        cmds.separator(height=8, style="none")
        cmds.button(
            label="E X P O R T",
            height=40,
            backgroundColor=(0.2, 0.62, 0.35),
            command=partial(self._on_export),
            annotation="Run the export for all checked formats",
        )
        cmds.separator(height=4, style="none")

        # --- Progress Bar ---
        cmds.rowLayout(
            numberOfColumns=2,
            adjustableColumn=1,
        )
        self.progress_bar = cmds.progressBar(
            maxValue=100, height=20, visible=False
        )
        self.progress_label = cmds.text(
            label="", align="right", font="smallPlainLabelFont",
            visible=False,
        )
        cmds.setParent("..")

        # --- Shared: Log ---
        self._build_log()

        # --- Version ---
        cmds.text(
            label="{}".format(TOOL_VERSION),
            align="right",
            font="smallObliqueLabelFont",
        )

        # Populate scene info and auto-refresh on scene open/save
        self._refresh_scene_info()
        self._scene_jobs = []
        for event in ("SceneOpened", "SceneSaved", "NewSceneOpened"):
            job_id = cmds.scriptJob(
                event=[event, self._refresh_scene_info],
                parent=self.window,
            )
            self._scene_jobs.append(job_id)

        # Frame range fields default to 1001/1001 until a camera is loaded
        # or the user clicks "Use Timeline Range".

    # --- UI Builders ---

    def _build_scene_info(self):
        cmds.frameLayout(
            label="Scene Info",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        self.scene_info_text = cmds.text(label="Scene: (none)", align="left")
        self.version_text = cmds.text(label="Version: (none)", align="left")
        cmds.setParent("..")
        cmds.setParent("..")

    def _build_export_root(self):
        cmds.frameLayout(
            label="Export Directory",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        self.export_root_field = cmds.textFieldButtonGrp(
            label="Path:",
            buttonLabel="Browse...",
            columnWidth3=(40, 300, 70),
            annotation="Root directory for all exported files",
        )
        cmds.textFieldButtonGrp(
            self.export_root_field,
            edit=True,
            buttonCommand=partial(self._browse_export_root),
        )
        self.version_field = cmds.textFieldGrp(
            label="Version Num (v##):",
            text="",
            columnWidth2=(108, 60),
            annotation=(
                "Version number appended to exported file names. "
                "Pre-populated from the scene filename."),
        )
        cmds.setParent("..")

    def _build_camera_track_tab(self):
        """Build Tab 1: Camera Track Export."""
        tab_col = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # Node Picker
        cmds.frameLayout(
            label="Node Picker  (In the outliner)",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        self.ct_camera_field = cmds.textFieldButtonGrp(
            label="Camera:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
            annotation="Select the camera to export",
        )
        cmds.textFieldButtonGrp(
            self.ct_camera_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "ct", "camera"),
        )

        # --- Dynamic geo group fields + buttons ---
        self.ct_geo_fields = []
        self.ct_geo_btn_row = None
        self.ct_geo_container = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=4
        )
        cmds.setParent("..")  # out of container

        # Add first geo field and buttons
        self._add_ct_geo_field()

        cmds.setParent("..")
        cmds.setParent("..")

        # Export Formats
        cmds.frameLayout(
            label="Export Formats",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        self.ct_ma_checkbox = cmds.checkBox(
            label="  Maya ASCII (.ma)", value=True,
            annotation="Export Maya ASCII scene file",
        )
        self.ct_jsx_checkbox = cmds.checkBox(
            label="  After Effects (.jsx + .obj)", value=True,
            annotation="Export After Effects JSX script with OBJ geometry",
        )
        self.ct_fbx_checkbox = cmds.checkBox(
            label="  FBX (.fbx)", value=True,
            annotation="Export FBX with baked animation",
        )
        self.ct_abc_checkbox = cmds.checkBox(
            label="  Alembic (.abc)", value=True,
            annotation="Export Alembic cache",
        )
        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=(130, 140),
            columnAttach=[(1, "left", 0), (2, "left", 0)],
        )
        self.ct_mov_checkbox = cmds.checkBox(
            label="  Playblast QC:", value=True,
            annotation="Export QC playblast",
        )
        self.ct_mov_format_menu = cmds.optionMenu(
            annotation="Choose playblast export format",
        )
        cmds.menuItem(label="H.264 (.mov)")
        cmds.menuItem(label="PNG Sequence")
        cmds.menuItem(label="H.264 (.mp4 Win)")
        if sys.platform == "win32":
            cmds.optionMenu(
                self.ct_mov_format_menu, edit=True,
                value="H.264 (.mp4 Win)")
        cmds.setParent("..")  # out of rowLayout
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.setParent("..")  # out of tab_col, back to tabLayout
        return tab_col

    def _build_matchmove_tab(self):
        """Build Tab 2: Matchmove Export."""
        tab_col = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # Node Picker
        cmds.frameLayout(
            label="Node Picker  (In the outliner)",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # --- Scene-level roles ---
        self.mm_camera_field = cmds.textFieldButtonGrp(
            label="Camera:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
            annotation="Select the camera to export",
        )
        cmds.textFieldButtonGrp(
            self.mm_camera_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "mm", "camera"),
        )

        # --- Dynamic static geo fields + buttons ---
        self.mm_static_geo_fields = []
        self.mm_static_geo_btn_row = None
        self.mm_static_geo_container = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=4
        )
        cmds.setParent("..")  # out of container

        # Add first static geo field and buttons
        self._add_mm_static_geo_field()

        # --- Separator ---
        cmds.separator(style="in", height=12)

        # --- Dynamic rig/geo pairs + buttons (all inside container) ---
        self.mm_rig_geo_pairs = []
        self.mm_btn_row = None
        self.mm_rig_geo_container = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=4
        )
        cmds.setParent("..")  # out of container

        # Add first pair and buttons
        self._add_rig_geo_pair()

        cmds.setParent("..")  # out of inner columnLayout
        cmds.setParent("..")  # out of frameLayout "Node Picker"

        # Export Formats
        cmds.frameLayout(
            label="Export Formats",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        self.mm_ma_checkbox = cmds.checkBox(
            label="  Maya ASCII (.ma)", value=True,
            annotation="Export Maya ASCII scene file",
        )
        self.mm_fbx_checkbox = cmds.checkBox(
            label="  FBX (.fbx)", value=True,
            annotation="Export FBX with baked animation",
        )
        self.mm_abc_checkbox = cmds.checkBox(
            label="  Alembic (.abc)", value=True,
            annotation="Export Alembic cache",
        )
        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=(130, 140),
            columnAttach=[(1, "left", 0), (2, "left", 0)],
        )
        self.mm_mov_checkbox = cmds.checkBox(
            label="  Playblast QC:", value=True,
            annotation="Export QC playblast",
        )
        self.mm_mov_format_menu = cmds.optionMenu(
            annotation="Choose playblast export format",
        )
        cmds.menuItem(label="H.264 (.mov)")
        cmds.menuItem(label="PNG Sequence")
        cmds.menuItem(label="H.264 (.mp4 Win)")
        if sys.platform == "win32":
            cmds.optionMenu(
                self.mm_mov_format_menu, edit=True,
                value="H.264 (.mp4 Win)")
        cmds.setParent("..")  # out of rowLayout
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.separator(style="in", height=8)
        cmds.rowLayout(
            numberOfColumns=3,
            columnWidth3=(120, 70, 1),
            columnAlign3=("left", "left", "left"),
            columnAttach=[(1, "left", 8), (2, "left", 0),
                          (3, "left", 0)],
        )
        self.tpose_checkbox = cmds.checkBox(
            label="  Include T Pose",
            value=True,
            changeCommand=partial(self._on_tpose_toggled),
            annotation="Include a T-pose frame before the animation start",
        )
        self.tpose_frame_field = cmds.intField(
            value=991,
            width=55,
            changeCommand=partial(self._on_tpose_frame_changed),
            annotation="Frame number for the T-pose",
        )
        cmds.text(label="")
        cmds.setParent("..")

        cmds.setParent("..")
        return tab_col

    def _build_face_track_tab(self):
        """Build Tab 3: Face Track Export."""
        tab_col = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # Node Picker
        cmds.frameLayout(
            label="Node Picker  (In the outliner)",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # --- Scene-level roles ---
        self.ft_camera_field = cmds.textFieldButtonGrp(
            label="Camera:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
            annotation="Select the camera to export",
        )
        cmds.textFieldButtonGrp(
            self.ft_camera_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "ft", "camera"),
        )

        self.ft_static_geo_field = cmds.textFieldButtonGrp(
            label="Static Geo:",
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
            annotation="Select static geometry group",
        )
        cmds.textFieldButtonGrp(
            self.ft_static_geo_field,
            edit=True,
            buttonCommand=partial(self._load_selection, "ft", "proxy"),
        )

        # --- Separator ---
        cmds.separator(style="in", height=12)

        # --- Dynamic face mesh entries + buttons (all inside container) ---
        self.ft_face_mesh_entries = []
        self.ft_btn_row = None
        self.ft_face_mesh_container = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=4
        )
        cmds.setParent("..")  # out of container

        # Add first face mesh entry and buttons
        self._add_face_mesh_entry()

        cmds.setParent("..")  # out of inner columnLayout
        cmds.setParent("..")  # out of frameLayout "Node Picker"

        # Export Formats
        cmds.frameLayout(
            label="Export Formats",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        self.ft_ma_checkbox = cmds.checkBox(
            label="  Maya ASCII (.ma)", value=True,
            annotation="Export Maya ASCII scene file",
        )
        self.ft_fbx_checkbox = cmds.checkBox(
            label="  FBX (.fbx)", value=True,
            annotation="Export FBX with baked blendshape animation",
        )
        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=(130, 140),
            columnAttach=[(1, "left", 0), (2, "left", 0)],
        )
        self.ft_mov_checkbox = cmds.checkBox(
            label="  Playblast QC:", value=True,
            annotation="Export QC playblast",
        )
        self.ft_mov_format_menu = cmds.optionMenu(
            annotation="Choose playblast export format",
        )
        cmds.menuItem(label="H.264 (.mov)")
        cmds.menuItem(label="PNG Sequence")
        cmds.menuItem(label="H.264 (.mp4 Win)")
        if sys.platform == "win32":
            cmds.optionMenu(
                self.ft_mov_format_menu, edit=True,
                value="H.264 (.mp4 Win)")
        cmds.setParent("..")  # out of rowLayout
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.setParent("..")
        return tab_col

    def _build_playblast_tab(self):
        """Build Tab 4: Playblast Settings (shared across all export tabs)."""
        tab_col = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        # --- Preview / Export Context ---
        cmds.rowLayout(
            numberOfColumns=2,
            columnWidth2=(110, 200),
            columnAttach=[(1, "left", 8), (2, "left", 0)],
        )
        cmds.text(label="Export Context:")
        self.pb_context_menu = cmds.optionMenu(
            annotation="Which export tab these settings apply to for preview",
        )
        cmds.menuItem(label="-- Choose --")
        cmds.menuItem(label="Camera Track")
        cmds.menuItem(label="Matchmove")
        cmds.menuItem(label="Face Track")
        cmds.setParent("..")

        cmds.separator(style="in", height=8)

        # --- General ---
        cmds.frameLayout(
            label="General",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        self.pb_aa16_cb = cmds.checkBox(
            label="  Anti-Aliasing 16x (increased RAM)",
            annotation=(
                "Sets VP2.0 MSAA to 16 samples instead of 8. "
                "Higher quality but requires more GPU memory."),
            value=False,
        )
        self.pb_far_clip = cmds.intSliderGrp(
            label="Far Clip:",
            field=True,
            minValue=10000,
            maxValue=2000000,
            fieldMinValue=1000,
            fieldMaxValue=10000000,
            value=800000,
            columnWidth3=(50, 70, 1),
            annotation="Camera far clipping plane for playblast",
        )
        cmds.separator(style="in", height=8)
        self.pb_raw_playblast_cb = cmds.checkBox(
            label="  Use Current Viewport Settings",
            annotation=(
                "Playblast uses your current VP2.0 settings "
                "without modifications"),
            value=False,
        )
        self.pb_custom_vt_cb = cmds.checkBox(
            label="  Use Custom View Transform",
            annotation=(
                "When checked, the playblast uses your current "
                "view transform instead of forcing Raw (sRGB)"),
            value=False,
        )
        self.pb_hud_overlay_cb = cmds.checkBox(
            label="  Show Frame / Focal Length HUD",
            annotation=(
                "Burn frame number and focal length "
                "into the playblast"),
            value=True,
        )
        cmds.setParent("..")
        cmds.setParent("..")

        # --- Camera Track ---
        cmds.frameLayout(
            label="Camera Track",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        self.pb_wireframe_shader_cb = cmds.checkBox(
            label="  useBackground Shader + Wireframe",
            annotation=(
                "Applies a useBackground shader to all geo with "
                "wireframe-on-shaded for the playblast"),
            value=True,
        )
        cmds.setParent("..")
        cmds.setParent("..")

        # --- Matchmove / Face Track ---
        cmds.frameLayout(
            label="Matchmove / Face Track",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        cmds.text(label="QC Checker Overlay", align="left",
                  font="smallBoldLabelFont")
        cmds.separator(style="none", height=4)
        self.pb_checker_color = cmds.colorSliderGrp(
            label="Color:",
            rgb=(0.6, 0.1, 0.1),
            columnWidth3=(40, 80, 1),
            annotation="Color of the UV checker overlay",
        )
        cmds.separator(style="none", height=6)
        self.pb_checker_scale = cmds.intSliderGrp(
            label="Scale:",
            field=True,
            minValue=1,
            maxValue=32,
            fieldMinValue=1,
            fieldMaxValue=32,
            value=15,
            columnWidth3=(40, 50, 1),
            annotation="Scale of the UV checker pattern",
        )
        cmds.separator(style="none", height=6)
        self.pb_checker_opacity = cmds.intSliderGrp(
            label="Blend:",
            field=True,
            minValue=0,
            maxValue=100,
            fieldMinValue=0,
            fieldMaxValue=100,
            value=30,
            columnWidth3=(40, 50, 1),
            annotation="Overlay blend opacity (0=plate only, "
            "100=full mesh overlay)",
        )
        cmds.setParent("..")
        cmds.setParent("..")

        # --- Preview ---
        cmds.separator(style="in", height=8)
        pb_preview_hint = cmds.text(
            label="Re-toggle preview to apply setting changes.",
            visible=False, font="smallObliqueLabelFont")
        self._preview_hints.append(pb_preview_hint)
        pb_preview_btn = cmds.button(
            label="Preview Playblast",
            height=28,
            command=partial(self._on_preview_playblast),
            annotation=(
                "Toggle live viewport preview of playblast settings. "
                "Click again to exit preview mode."),
        )
        self._preview_buttons.append(pb_preview_btn)

        cmds.setParent("..")  # out of tab_col, back to tabLayout
        return tab_col

    def _build_frame_range(self):
        cmds.frameLayout(
            label="Frame Range",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
        cmds.rowLayout(
            numberOfColumns=5,
            columnWidth5=(60, 70, 20, 60, 70),
            columnAlign5=("right", "left", "center", "right", "left"),
        )
        cmds.text(label="Start: ")
        self.start_frame_field = cmds.intField(value=1001, width=65, annotation="First frame of the export range")
        cmds.text(label="")
        cmds.text(label="End: ")
        self.end_frame_field = cmds.intField(value=1001, width=65, annotation="Last frame of the export range")
        cmds.setParent("..")
        cmds.button(
            label="Use Timeline Range",
            command=partial(self._set_timeline_range),
            annotation="Set start/end frames from the scene timeline",
        )
        cmds.setParent("..")
        cmds.setParent("..")

    def _build_log(self):
        cmds.frameLayout(
            label="Status",
            collapsable=True,
            marginWidth=8,
            marginHeight=6,
        )
        self.log_field = cmds.scrollField(
            editable=False, wordWrap=True, height=120, text=""
        )
        cmds.setParent("..")

    # --- Tab Helpers ---

    def _get_active_tab(self):
        """Return the active export tab identifier based on selected tab index.

        If the Playblast Settings tab (4) is active, returns the last
        export tab the user was on so preview/export work correctly.
        """
        idx = cmds.tabLayout(self.tab_layout, query=True, selectTabIndex=True)
        if idx == 1:
            self._last_export_tab = TAB_CAMERA_TRACK
            return TAB_CAMERA_TRACK
        elif idx == 2:
            self._last_export_tab = TAB_MATCHMOVE
            return TAB_MATCHMOVE
        elif idx == 3:
            self._last_export_tab = TAB_FACE_TRACK
            return TAB_FACE_TRACK
        # Tab 4 = Playblast Settings — use context menu selection
        if self.pb_context_menu:
            ctx = cmds.optionMenu(self.pb_context_menu, query=True, value=True)
            if ctx == "Camera Track":
                return TAB_CAMERA_TRACK
            elif ctx == "Matchmove":
                return TAB_MATCHMOVE
            elif ctx == "Face Track":
                return TAB_FACE_TRACK
        # "-- Choose --" or unset
        return None

    # --- Callbacks ---

    def _browse_export_root(self, *args):
        result = cmds.fileDialog2(
            fileMode=3, caption="Select Export Root Directory"
        )
        if result:
            cmds.textFieldButtonGrp(
                self.export_root_field, edit=True, text=result[0]
            )

    def _load_selection_into(self, target_field, role, *args):
        """Validate the current selection and load it into a field.

        Args:
            target_field: The textFieldButtonGrp widget to populate.
            role: "camera", "geo", "rig", or "proxy" — drives validation.
        """
        sel = cmds.ls(selection=True, long=False)
        if not sel:
            cmds.confirmDialog(
                title="No Selection",
                message="Export Genie {}\n\nNothing is selected. Please select an object first.".format(
                    TOOL_VERSION),
                button=["OK"],
            )
            return

        obj = sel[0]

        # Validate based on role
        if role == "camera":
            shapes = cmds.listRelatives(obj, shapes=True, type="camera") or []
            if not shapes:
                if cmds.nodeType(obj) == "camera":
                    parents = cmds.listRelatives(obj, parent=True)
                    if parents:
                        obj = parents[0]
                else:
                    cmds.confirmDialog(
                        title="Invalid Selection",
                        message="Export Genie {}\n\n'{}' is not a camera. Please select a camera.".format(
                            TOOL_VERSION, obj),
                        button=["OK"],
                    )
                    return
        else:
            # geo, rig, proxy — must be a transform
            if cmds.nodeType(obj) != "transform":
                role_labels = {
                    "geo": "geo group/root",
                    "rig": "rig root",
                    "proxy": "static geo root",
                }
                cmds.confirmDialog(
                    title="Invalid Selection",
                    message="Export Genie {}\n\n'{}' is not a transform node. Please select the {}.".format(
                        TOOL_VERSION, obj, role_labels.get(role, role)
                    ),
                    button=["OK"],
                )
                return

        cmds.textFieldButtonGrp(target_field, edit=True, text=obj)

        # When a camera is loaded, auto-populate frame range from its animation
        if role == "camera":
            self._set_frame_range_from_camera(obj)

    def _set_frame_range_from_camera(self, cam_xform):
        """Set start/end frames from the camera's animation curve extents.

        Queries all anim curves connected to the camera hierarchy
        (transform, shape, and ancestors).  Falls back to AlembicNode
        time range for cache-driven cameras.
        """
        keys = []

        # Collect all nodes to check: the transform, its shapes,
        # and every ancestor up to the root
        nodes_to_check = [cam_xform]
        shapes = cmds.listRelatives(
            cam_xform, shapes=True, type="camera") or []
        nodes_to_check.extend(shapes)
        node = cam_xform
        while True:
            parents = cmds.listRelatives(
                node, parent=True, fullPath=False)
            if not parents:
                break
            node = parents[0]
            nodes_to_check.append(node)

        # Query keyframes from all connected animCurve nodes
        for n in nodes_to_check:
            anim_curves = cmds.listConnections(
                n, source=True, destination=False,
                type="animCurve") or []
            for ac in anim_curves:
                ac_keys = cmds.keyframe(
                    ac, query=True, timeChange=True) or []
                keys.extend(ac_keys)

        # Alembic-driven cameras: no keyframes, but an AlembicNode
        # holds the authoritative time range
        if not keys:
            all_descendants = cmds.listRelatives(
                cam_xform, allDescendents=True,
                fullPath=True) or [cam_xform]
            all_descendants.append(cam_xform)
            for desc in all_descendants:
                conns = cmds.listConnections(
                    desc, source=True, type="AlembicNode") or []
                for abc_node in conns:
                    try:
                        start_t = cmds.getAttr(
                            abc_node + ".startFrame")
                        end_t = cmds.getAttr(
                            abc_node + ".endFrame")
                        keys.extend([start_t, end_t])
                    except Exception:
                        pass
                if keys:
                    break

        if keys:
            first_frame = int(min(keys))
            last_frame = int(max(keys))
            cmds.intField(
                self.start_frame_field, edit=True, value=first_frame)
            cmds.intField(
                self.end_frame_field, edit=True, value=last_frame)

    def _load_selection(self, tab_prefix, role, *args):
        """Load the current viewport selection into the appropriate field.

        Args:
            tab_prefix: "ct" for Camera Track, "mm" for Matchmove, "ft" for Face Track.
            role: "camera", "geo", "rig", or "proxy".
        """
        if tab_prefix == "ct":
            field_map = {
                "camera": self.ct_camera_field,
            }
        elif tab_prefix == "ft":
            field_map = {
                "camera": self.ft_camera_field,
                "proxy": self.ft_static_geo_field,
            }
        else:
            field_map = {
                "camera": self.mm_camera_field,
            }

        target_field = field_map.get(role)
        if not target_field:
            return

        self._load_selection_into(target_field, role)

    # --- Camera Track dynamic geo group fields ---

    def _rebuild_ct_geo_buttons(self):
        """Recreate the +/- button row at the bottom of the CT geo container."""
        if self.ct_geo_btn_row:
            cmds.deleteUI(self.ct_geo_btn_row)
            self.ct_geo_btn_row = None

        cmds.setParent(self.ct_geo_container)
        self.ct_geo_btn_row = cmds.rowLayout(
            numberOfColumns=3,
            columnWidth3=(70, 30, 30),
            columnAlign3=("right", "center", "center"),
        )
        cmds.text(label="")
        cmds.button(
            label="+", width=26,
            command=partial(self._add_ct_geo_field),
            annotation="Add another geo group",
        )
        cmds.button(
            label="-", width=26,
            visible=(len(self.ct_geo_fields) >= 2),
            command=partial(self._remove_ct_geo_field),
            annotation="Remove the last geo group",
        )
        cmds.setParent("..")  # out of rowLayout
        cmds.setParent("..")  # out of container

    def _add_ct_geo_field(self, *args):
        """Add a new Geo Group picker field to the camera track tab."""
        if self.ct_geo_btn_row:
            cmds.deleteUI(self.ct_geo_btn_row)
            self.ct_geo_btn_row = None

        idx = len(self.ct_geo_fields) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        cmds.setParent(self.ct_geo_container)
        row = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        field = cmds.textFieldButtonGrp(
            label="Geo Group{}:".format(suffix),
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
            annotation="Select a top-level geo group to export",
        )
        cmds.textFieldButtonGrp(
            field, edit=True,
            buttonCommand=partial(self._load_selection_into, field, "geo"),
        )

        cmds.setParent("..")  # out of row columnLayout
        cmds.setParent("..")  # out of container

        self.ct_geo_fields.append({
            "field": field,
            "row": row,
        })

        self._rebuild_ct_geo_buttons()

    def _remove_ct_geo_field(self, *args):
        """Remove the last Geo Group picker field from camera track tab."""
        if len(self.ct_geo_fields) <= 1:
            return

        entry = self.ct_geo_fields.pop()
        cmds.deleteUI(entry["row"])

        self._rebuild_ct_geo_buttons()

    # --- Matchmove dynamic rig/geo pairs ---

    def _rebuild_rig_geo_buttons(self):
        """Recreate the +/- button row at the bottom of the rig/geo container."""
        if self.mm_btn_row:
            cmds.deleteUI(self.mm_btn_row)
            self.mm_btn_row = None

        cmds.setParent(self.mm_rig_geo_container)
        self.mm_btn_row = cmds.rowLayout(
            numberOfColumns=3,
            columnWidth3=(70, 30, 30),
            columnAlign3=("right", "center", "center"),
        )
        cmds.text(label="")
        self.mm_add_btn = cmds.button(
            label="+", width=26,
            command=partial(self._add_rig_geo_pair),
            annotation="Add another rig/geo pair",
        )
        self.mm_minus_btn = cmds.button(
            label="-", width=26,
            visible=(len(self.mm_rig_geo_pairs) >= 2),
            command=partial(self._remove_rig_geo_pair),
            annotation="Remove the last rig/geo pair",
        )
        cmds.setParent("..")  # out of rowLayout
        cmds.setParent("..")  # out of container

    def _add_rig_geo_pair(self, *args):
        """Add a new Main Rig Group / Mesh Group pair to the matchmove tab."""
        # Remove button row so the new pair is inserted before it
        if self.mm_btn_row:
            cmds.deleteUI(self.mm_btn_row)
            self.mm_btn_row = None

        idx = len(self.mm_rig_geo_pairs) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        cmds.setParent(self.mm_rig_geo_container)
        row = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        rig_field = cmds.textFieldButtonGrp(
            label="Main Rig Group{}:".format(suffix),
            buttonLabel="<< Load Sel",
            columnWidth3=(90, 240, 80),
            editable=False,
            annotation="Select the control rig group",
        )
        cmds.textFieldButtonGrp(
            rig_field, edit=True,
            buttonCommand=partial(self._load_selection_into, rig_field, "rig"),
        )

        geo_field = cmds.textFieldButtonGrp(
            label="Mesh Group{}:".format(suffix),
            buttonLabel="<< Load Sel",
            columnWidth3=(90, 240, 80),
            editable=False,
            annotation="Select the animated geo group",
        )
        cmds.textFieldButtonGrp(
            geo_field, edit=True,
            buttonCommand=partial(self._load_selection_into, geo_field, "geo"),
        )

        cmds.setParent("..")  # out of row columnLayout
        cmds.setParent("..")  # out of container

        self.mm_rig_geo_pairs.append({
            "rig_field": rig_field,
            "geo_field": geo_field,
            "row": row,
        })

        # Rebuild buttons at the bottom
        self._rebuild_rig_geo_buttons()

    def _remove_rig_geo_pair(self, *args):
        """Remove the last Main Rig Group / Mesh Group pair."""
        if len(self.mm_rig_geo_pairs) <= 1:
            return

        entry = self.mm_rig_geo_pairs.pop()
        cmds.deleteUI(entry["row"])

        # Rebuild buttons (updates minus visibility)
        self._rebuild_rig_geo_buttons()

    # --- Matchmove dynamic static geo fields ---

    def _rebuild_mm_static_geo_buttons(self):
        """Recreate the +/- button row at the bottom of the MM static geo container."""
        if self.mm_static_geo_btn_row:
            cmds.deleteUI(self.mm_static_geo_btn_row)
            self.mm_static_geo_btn_row = None

        cmds.setParent(self.mm_static_geo_container)
        self.mm_static_geo_btn_row = cmds.rowLayout(
            numberOfColumns=3,
            columnWidth3=(70, 30, 30),
            columnAlign3=("right", "center", "center"),
        )
        cmds.text(label="")
        cmds.button(
            label="+", width=26,
            command=partial(self._add_mm_static_geo_field),
            annotation="Add another static geo group",
        )
        cmds.button(
            label="-", width=26,
            visible=(len(self.mm_static_geo_fields) >= 2),
            command=partial(self._remove_mm_static_geo_field),
            annotation="Remove the last static geo group",
        )
        cmds.setParent("..")  # out of rowLayout
        cmds.setParent("..")  # out of container

    def _add_mm_static_geo_field(self, *args):
        """Add a new Static Geo picker field to the matchmove tab."""
        if self.mm_static_geo_btn_row:
            cmds.deleteUI(self.mm_static_geo_btn_row)
            self.mm_static_geo_btn_row = None

        idx = len(self.mm_static_geo_fields) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        cmds.setParent(self.mm_static_geo_container)
        row = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        field = cmds.textFieldButtonGrp(
            label="Static Geo{}:".format(suffix),
            buttonLabel="<< Load Sel",
            columnWidth3=(70, 260, 80),
            editable=False,
            annotation="Select static/proxy geometry group",
        )
        cmds.textFieldButtonGrp(
            field, edit=True,
            buttonCommand=partial(self._load_selection_into, field, "proxy"),
        )

        cmds.setParent("..")  # out of row columnLayout
        cmds.setParent("..")  # out of container

        self.mm_static_geo_fields.append({
            "field": field,
            "row": row,
        })

        self._rebuild_mm_static_geo_buttons()

    def _remove_mm_static_geo_field(self, *args):
        """Remove the last Static Geo picker field from matchmove tab."""
        if len(self.mm_static_geo_fields) <= 1:
            return

        entry = self.mm_static_geo_fields.pop()
        cmds.deleteUI(entry["row"])

        self._rebuild_mm_static_geo_buttons()

    # --- Face Track dynamic face mesh entries ---

    def _rebuild_face_mesh_buttons(self):
        """Recreate the +/- button row at the bottom of the face mesh container."""
        if self.ft_btn_row:
            cmds.deleteUI(self.ft_btn_row)
            self.ft_btn_row = None

        cmds.setParent(self.ft_face_mesh_container)
        self.ft_btn_row = cmds.rowLayout(
            numberOfColumns=3,
            columnWidth3=(70, 30, 30),
            columnAlign3=("right", "center", "center"),
        )
        cmds.text(label="")
        self.ft_add_btn = cmds.button(
            label="+", width=26,
            command=partial(self._add_face_mesh_entry),
            annotation="Add another face mesh entry",
        )
        self.ft_minus_btn = cmds.button(
            label="-", width=26,
            visible=(len(self.ft_face_mesh_entries) >= 2),
            command=partial(self._remove_face_mesh_entry),
            annotation="Remove the last face mesh entry",
        )
        cmds.setParent("..")  # out of rowLayout
        cmds.setParent("..")  # out of container

    def _add_face_mesh_entry(self, *args):
        """Add a new Face Mesh picker field to the face track tab."""
        if self.ft_btn_row:
            cmds.deleteUI(self.ft_btn_row)
            self.ft_btn_row = None

        idx = len(self.ft_face_mesh_entries) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        cmds.setParent(self.ft_face_mesh_container)
        row = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        field = cmds.textFieldButtonGrp(
            label="Face Mesh{}:".format(suffix),
            buttonLabel="<< Load Sel",
            columnWidth3=(90, 240, 80),
            editable=False,
            annotation="Select a face mesh to export",
        )
        cmds.textFieldButtonGrp(
            field, edit=True,
            buttonCommand=partial(self._load_selection_into, field, "geo"),
        )

        cmds.setParent("..")  # out of row columnLayout
        cmds.setParent("..")  # out of container

        self.ft_face_mesh_entries.append({
            "field": field,
            "row": row,
        })

        self._rebuild_face_mesh_buttons()

    def _remove_face_mesh_entry(self, *args):
        """Remove the last Face Mesh picker field."""
        if len(self.ft_face_mesh_entries) <= 1:
            return

        entry = self.ft_face_mesh_entries.pop()
        cmds.deleteUI(entry["row"])

        self._rebuild_face_mesh_buttons()

    def _set_timeline_range(self, *args):
        start = cmds.playbackOptions(query=True, animationStartTime=True)
        end = cmds.playbackOptions(query=True, animationEndTime=True)
        cmds.intField(self.start_frame_field, edit=True,
                       value=int(start))
        cmds.intField(self.end_frame_field, edit=True, value=int(end))

    def _on_tpose_toggled(self, checked, *args):
        """When Include T Pose is toggled (no longer modifies start frame).

        The T-pose frame is handled internally during export — FBX and ABC
        extend their range to include the T-pose, while .ma and QC playblast
        keep the original timeline range.
        """
        pass

    def _on_tpose_frame_changed(self, value, *args):
        """When the T-pose frame number changes (no UI side-effects)."""
        pass

    def _refresh_scene_info(self):
        scene_path = cmds.file(query=True, sceneName=True)
        if scene_path:
            scene_short = cmds.file(
                query=True, sceneName=True, shortName=True
            )
            cmds.text(
                self.scene_info_text,
                edit=True,
                label="Scene: " + scene_short,
            )
            ver_str, _ = VersionParser.parse(scene_short)
            if ver_str:
                cmds.text(
                    self.version_text,
                    edit=True,
                    label="Version: {} (detected)".format(ver_str),
                )
                cmds.textFieldGrp(
                    self.version_field, edit=True, text=ver_str)
            else:
                cmds.text(
                    self.version_text,
                    edit=True,
                    label="Version: (none detected \u2014 will default to v01)",
                )
                cmds.textFieldGrp(
                    self.version_field, edit=True, text="v01")
        else:
            cmds.text(
                self.scene_info_text,
                edit=True,
                label="Scene: (unsaved scene)",
            )
            cmds.text(
                self.version_text,
                edit=True,
                label="Version: (save scene first)",
            )
            cmds.textFieldGrp(
                self.version_field, edit=True, text="v01")

    def _log(self, message):
        current = cmds.scrollField(self.log_field, query=True, text=True)
        if current:
            updated = current + "\n" + message
        else:
            updated = message
        cmds.scrollField(self.log_field, edit=True, text=updated)
        cmds.scrollField(
            self.log_field, edit=True, insertionPosition=len(updated)
        )

    def _log_result(self, label, success):
        """Append a single-line task result to the log.

        success=True  -> 'MA ... done'
        success=False -> 'MA ... FAILED  (see Script Editor)'
        """
        if success:
            self._log("{} complete.".format(label))
        else:
            self._log("{} failed. See Script Editor.".format(label))

    # --- Progress Bar ---

    def _reset_progress(self, total_steps):
        """Show and reset the progress bar for a new export run."""
        self._progress_total = max(total_steps, 1)
        self._progress_done = 0
        cmds.progressBar(
            self.progress_bar, edit=True, progress=0, visible=True
        )
        cmds.text(
            self.progress_label, edit=True, label="0%", visible=True
        )
        cmds.refresh(force=True)

    def _advance_progress(self):
        """Advance the progress bar by one step."""
        self._progress_done += 1
        pct = int(
            (self._progress_done / float(self._progress_total)) * 100
        )
        cmds.progressBar(
            self.progress_bar, edit=True, progress=min(pct, 100)
        )
        cmds.text(
            self.progress_label, edit=True,
            label="{}%".format(min(pct, 100))
        )
        cmds.refresh(force=True)

    def _hide_progress(self):
        """Hide the progress bar after export completes."""
        cmds.progressBar(self.progress_bar, edit=True, visible=False)
        cmds.text(self.progress_label, edit=True, visible=False)

    # --- Validation ---

    def _validate_shared(self):
        """Validate settings shared across both tabs.

        Returns:
            tuple: (errors, warnings, export_root, version_str, scene_base,
                    start_frame, end_frame)
        """
        errors = []
        warnings = []

        scene_path = cmds.file(query=True, sceneName=True)
        if not scene_path:
            errors.append("Scene has not been saved. Please save first.")

        export_root = cmds.textFieldButtonGrp(
            self.export_root_field, query=True, text=True
        ).strip()
        if not export_root:
            errors.append("Export root directory is not set.")
        elif not os.path.isdir(export_root):
            errors.append(
                "Export root directory does not exist:\n" + export_root
            )

        start_frame = cmds.intField(
            self.start_frame_field, query=True, value=True
        )
        end_frame = cmds.intField(
            self.end_frame_field, query=True, value=True
        )
        if end_frame <= start_frame:
            errors.append("End frame must be greater than start frame.")

        version_str = cmds.textFieldGrp(
            self.version_field, query=True, text=True).strip()
        if not version_str:
            version_str = None
        scene_base = None
        if scene_path:
            scene_short = cmds.file(
                query=True, sceneName=True, shortName=True
            )
            scene_base = VersionParser.get_scene_base_name(scene_short)
            if not version_str:
                warnings.append(
                    "Version Num field is empty.\n"
                    "Will default to v01."
                )

        return (errors, warnings, export_root, version_str, scene_base,
                start_frame, end_frame)

    def _validate_camera_track(self):
        """Validate Camera Track tab fields. Returns (errors, warnings)."""
        errors, warnings, export_root, version_str, scene_base, \
            start_frame, end_frame = self._validate_shared()

        do_ma = cmds.checkBox(self.ct_ma_checkbox, query=True, value=True)
        do_jsx = cmds.checkBox(self.ct_jsx_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.ct_fbx_checkbox, query=True, value=True)
        do_abc = cmds.checkBox(self.ct_abc_checkbox, query=True, value=True)
        do_mov = cmds.checkBox(self.ct_mov_checkbox, query=True, value=True)
        if not (do_ma or do_jsx or do_fbx or do_abc or do_mov):
            errors.append("No export format selected.")

        camera = cmds.textFieldButtonGrp(
            self.ct_camera_field, query=True, text=True
        ).strip()

        # Gather all geo group fields
        geo_roots = []
        for i, entry in enumerate(self.ct_geo_fields):
            g = cmds.textFieldButtonGrp(
                entry["field"], query=True, text=True
            ).strip()
            if g:
                geo_roots.append(g)
            suffix = "" if i == 0 else " {}".format(i + 1)
            if g and not cmds.objExists(g):
                errors.append(
                    "Geo Group{} '{}' no longer exists in the scene.".format(
                        suffix, g))

        has_geo = bool(geo_roots)
        if do_ma and not camera and not has_geo:
            errors.append(
                "MA export enabled but no Camera or Geo Node assigned."
            )
        if do_jsx and not camera and not has_geo:
            errors.append(
                "JSX export enabled but no Camera or Geo Node assigned."
            )
        if do_fbx and not (camera or has_geo):
            errors.append(
                "FBX export enabled but no Camera or Geo Node assigned."
            )
        if do_abc and not (camera or has_geo):
            errors.append(
                "Alembic export enabled but no Camera or Geo Node assigned."
            )

        if camera and not cmds.objExists(camera):
            errors.append(
                "Camera '{}' no longer exists in the scene.".format(camera)
            )

        # Name-collision checks
        assigned = []
        if camera:
            assigned.append(("Camera", camera))
        for i, g in enumerate(geo_roots):
            suffix = "" if i == 0 else " {}".format(i + 1)
            assigned.append(("Geo Group{}".format(suffix), g))
        self._check_name_collisions(errors, assigned)

        if do_jsx:
            for g in geo_roots:
                if g and cmds.objExists(g):
                    self._check_obj_name_collisions(errors, g, camera)

        return errors, warnings

    def _validate_matchmove(self):
        """Validate Matchmove tab fields. Returns (errors, warnings)."""
        errors, warnings, export_root, version_str, scene_base, \
            start_frame, end_frame = self._validate_shared()

        do_ma = cmds.checkBox(self.mm_ma_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.mm_fbx_checkbox, query=True, value=True)
        do_abc = cmds.checkBox(self.mm_abc_checkbox, query=True, value=True)
        do_mov = cmds.checkBox(self.mm_mov_checkbox, query=True, value=True)
        if not (do_ma or do_fbx or do_abc or do_mov):
            errors.append("No export format selected.")

        camera = cmds.textFieldButtonGrp(
            self.mm_camera_field, query=True, text=True
        ).strip()

        # Gather all static geo fields
        proxy_geos = []
        for i, entry in enumerate(self.mm_static_geo_fields):
            pg = cmds.textFieldButtonGrp(
                entry["field"], query=True, text=True
            ).strip()
            if pg:
                proxy_geos.append(pg)
            suffix = "" if i == 0 else " {}".format(i + 1)
            if pg and not cmds.objExists(pg):
                errors.append(
                    "Static Geo{} '{}' no longer exists in the scene.".format(
                        suffix, pg))

        # Gather rig/geo pairs
        rig_roots = []
        geo_roots = []
        for i, pair in enumerate(self.mm_rig_geo_pairs):
            r = cmds.textFieldButtonGrp(
                pair["rig_field"], query=True, text=True
            ).strip()
            g = cmds.textFieldButtonGrp(
                pair["geo_field"], query=True, text=True
            ).strip()
            if r:
                rig_roots.append(r)
            if g:
                geo_roots.append(g)
            # Validate existence
            suffix = "" if i == 0 else " {}".format(i + 1)
            if r and not cmds.objExists(r):
                errors.append(
                    "Main Rig Group{} '{}' no longer exists in the scene.".format(
                        suffix, r))
            if g and not cmds.objExists(g):
                errors.append(
                    "Mesh Group{} '{}' no longer exists in the scene.".format(
                        suffix, g))

        if do_ma and not any(geo_roots + rig_roots + [camera]):
            errors.append(
                "MA export enabled but no roles assigned (nothing to export)."
            )
        if do_fbx and not (geo_roots or rig_roots):
            errors.append(
                "FBX export enabled but no Mesh Group or Main Rig Group assigned."
            )
        if do_abc and not geo_roots:
            errors.append("Alembic export enabled but no Mesh Group assigned.")

        if camera and not cmds.objExists(camera):
            errors.append(
                "Camera '{}' no longer exists in the scene.".format(camera)
            )

        # Name-collision checks
        assigned = []
        if camera:
            assigned.append(("Camera", camera))
        for i, pg in enumerate(proxy_geos):
            suffix = "" if i == 0 else " {}".format(i + 1)
            assigned.append(("Static Geo{}".format(suffix), pg))
        for i, pair in enumerate(self.mm_rig_geo_pairs):
            r = cmds.textFieldButtonGrp(
                pair["rig_field"], query=True, text=True
            ).strip()
            g = cmds.textFieldButtonGrp(
                pair["geo_field"], query=True, text=True
            ).strip()
            suffix = "" if i == 0 else " {}".format(i + 1)
            if r:
                assigned.append(("Main Rig Group{}".format(suffix), r))
            if g:
                assigned.append(("Mesh Group{}".format(suffix), g))
        self._check_name_collisions(errors, assigned)

        return errors, warnings

    def _validate_face_track(self):
        """Validate Face Track tab fields. Returns (errors, warnings)."""
        errors, warnings, export_root, version_str, scene_base, \
            start_frame, end_frame = self._validate_shared()

        do_ma = cmds.checkBox(self.ft_ma_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.ft_fbx_checkbox, query=True, value=True)
        do_mov = cmds.checkBox(self.ft_mov_checkbox, query=True, value=True)
        if not (do_ma or do_fbx or do_mov):
            errors.append("No export format selected.")

        camera = cmds.textFieldButtonGrp(
            self.ft_camera_field, query=True, text=True
        ).strip()
        static_geo = cmds.textFieldButtonGrp(
            self.ft_static_geo_field, query=True, text=True
        ).strip()

        # Gather face meshes
        face_meshes = []
        for i, entry in enumerate(self.ft_face_mesh_entries):
            fm = cmds.textFieldButtonGrp(
                entry["field"], query=True, text=True
            ).strip()
            if fm:
                face_meshes.append(fm)
            suffix = "" if i == 0 else " {}".format(i + 1)
            if fm and not cmds.objExists(fm):
                errors.append(
                    "Face Mesh{} '{}' no longer exists in the scene.".format(
                        suffix, fm))

        if do_fbx and not face_meshes:
            errors.append(
                "FBX export enabled but no Face Mesh assigned."
            )
        if do_ma and not any(face_meshes + [camera]):
            errors.append(
                "MA export enabled but no roles assigned (nothing to export)."
            )

        for role_name, value in [
            ("Camera", camera),
            ("Static Geo", static_geo),
        ]:
            if value and not cmds.objExists(value):
                errors.append(
                    "{} '{}' no longer exists in the scene.".format(
                        role_name, value
                    )
                )

        # Name-collision checks
        assigned = []
        if camera:
            assigned.append(("Camera", camera))
        if static_geo:
            assigned.append(("Static Geo", static_geo))
        for i, entry in enumerate(self.ft_face_mesh_entries):
            fm = cmds.textFieldButtonGrp(
                entry["field"], query=True, text=True
            ).strip()
            suffix = "" if i == 0 else " {}".format(i + 1)
            if fm:
                assigned.append(("Face Mesh{}".format(suffix), fm))
        self._check_name_collisions(errors, assigned)

        return errors, warnings

    # --- Name-collision helpers ---

    @staticmethod
    def _check_name_collisions(errors, assigned_nodes):
        """Detect duplicate picks and cam_main rename conflicts.

        Args:
            errors: List to append error strings to.
            assigned_nodes: List of (role_label, node_name) tuples.
        """
        # Duplicate picks — same node in two or more role fields.
        seen = {}
        for role, node in assigned_nodes:
            if node in seen:
                errors.append(
                    "Name collision: '{}' is assigned to both {} and {}.".format(
                        node, seen[node], role
                    )
                )
            else:
                seen[node] = role

        # cam_main conflict — a different node already has that name.
        cameras = [n for r, n in assigned_nodes if "camera" in r.lower()]
        for cam in cameras:
            if cam != "cam_main" and cmds.objExists("cam_main"):
                errors.append(
                    "Name collision: A node named 'cam_main' already exists. "
                    "The camera will be renamed to 'cam_main' during export, "
                    "which would conflict."
                )
                break

    @staticmethod
    def _check_obj_name_collisions(errors, geo_root, camera):
        """Detect duplicate short names among geo children (OBJ export).

        Args:
            errors: List to append error strings to.
            geo_root: Top-level geo group node.
            camera: Camera node name (excluded from children).
        """
        children = cmds.listRelatives(
            geo_root, children=True, type="transform"
        ) or []
        if not children:
            return

        # Apply same filters used during export.
        if camera:
            children = [
                c for c in children
                if not Exporter._is_descendant_of(camera, c)
            ]
        children = [
            c for c in children
            if "chisels" not in c.lower()
            and "nulls" not in c.lower()
        ]

        # Check for duplicate short names.
        name_count = {}
        for c in children:
            short = c.rsplit("|", 1)[-1].rsplit(":", 1)[-1]
            name_count.setdefault(short, []).append(c)
        for short, nodes in name_count.items():
            if len(nodes) > 1:
                errors.append(
                    "Name collision: Multiple geo children share the "
                    "name '{}'. OBJ files would overwrite each other. "
                    "Please rename them to be unique.".format(short)
                )

    # --- Export Orchestration ---

    def _on_export(self, *args):
        """Main export callback — dispatches to active tab's export."""
        if self._preview_active:
            self._exit_preview_mode()
        cmds.scrollField(self.log_field, edit=True, text="")

        active_tab = self._get_active_tab()
        if active_tab is None:
            cmds.confirmDialog(
                title="Export Context Required",
                message="Please select an Export Context (Camera Track, "
                        "Matchmove, or Face Track) in the Playblast "
                        "Settings tab before exporting.",
                button=["OK"],
                defaultButton="OK",
            )
            return
        if active_tab == TAB_CAMERA_TRACK:
            self._export_camera_track()
        elif active_tab == TAB_MATCHMOVE:
            self._export_matchmove()
        else:
            self._export_face_track()

    def _on_window_close(self, *args):
        """Clean up preview mode when the window is closed."""
        if self._preview_active:
            self._exit_preview_mode()

    # ------------------------------------------------------------------
    # Preview Playblast
    # ------------------------------------------------------------------

    def _on_preview_playblast(self, *args):
        """Toggle live viewport preview of playblast settings."""
        if self._preview_active:
            self._exit_preview_mode()
        else:
            self._enter_preview_mode()

    def _enter_preview_mode(self):
        """Apply all playblast viewport overrides for live preview."""
        active_tab = self._get_active_tab()
        if active_tab is None:
            cmds.confirmDialog(
                title="Export Context Required",
                message="Please select an Export Context (Camera Track, "
                        "Matchmove, or Face Track) in the Playblast "
                        "Settings tab before previewing.",
                button=["OK"],
                defaultButton="OK",
            )
            return

        # --- Resolve camera ---
        if active_tab == TAB_CAMERA_TRACK:
            camera = cmds.textFieldButtonGrp(
                self.ct_camera_field, query=True, text=True).strip()
        elif active_tab == TAB_MATCHMOVE:
            camera = cmds.textFieldButtonGrp(
                self.mm_camera_field, query=True, text=True).strip()
        else:
            camera = cmds.textFieldButtonGrp(
                self.ft_camera_field, query=True, text=True).strip()

        if not camera or not cmds.objExists(camera):
            cmds.confirmDialog(
                title="Preview Playblast",
                message="Export Genie {}\n\n"
                        "No valid camera assigned. Please load a "
                        "camera in the Node Picker first.".format(
                            TOOL_VERSION),
                button=["OK"],
            )
            return

        # Update buttons immediately so user sees feedback first
        self._preview_active = True
        for btn in self._preview_buttons:
            try:
                cmds.button(btn, edit=True,
                            label="Exit Preview",
                            backgroundColor=[0.9, 0.5, 0.5])
            except Exception:
                pass
        for hint in self._preview_hints:
            try:
                cmds.text(hint, edit=True, visible=True)
            except Exception:
                pass
        cmds.refresh(currentView=True)

        # Read shared playblast settings from Playblast Settings tab
        raw_pb = cmds.checkBox(
            self.pb_raw_playblast_cb, query=True, value=True)
        custom_vt = cmds.checkBox(
            self.pb_custom_vt_cb, query=True, value=True)
        far_clip = cmds.intSliderGrp(
            self.pb_far_clip, query=True, value=True)

        state = {"tab": active_tab, "raw_playblast": raw_pb}

        # --- Find model panel ---
        model_panel = None
        for panel in (cmds.getPanel(visiblePanels=True) or []):
            if cmds.getPanel(typeOf=panel) == "modelPanel":
                model_panel = panel
                break
        if not model_panel:
            panels = cmds.getPanel(type="modelPanel") or []
            if panels:
                model_panel = panels[0]
        state["model_panel"] = model_panel

        # --- Switch camera ---
        if camera and model_panel:
            state["original_cam"] = cmds.modelPanel(
                model_panel, query=True, camera=True)
            cmds.lookThru(model_panel, camera)
        state["camera"] = camera

        # --- Disable pan/zoom, set far clip ---
        if camera:
            cam_shapes = cmds.listRelatives(
                camera, shapes=True, type="camera") or []
            if cam_shapes:
                cs = cam_shapes[0]
                try:
                    state["original_pan_zoom"] = cmds.getAttr(
                        cs + ".panZoomEnabled")
                    cmds.setAttr(cs + ".panZoomEnabled", False)
                except Exception:
                    pass
                try:
                    state["original_far_clip"] = cmds.getAttr(
                        cs + ".farClipPlane")
                    cmds.setAttr(cs + ".farClipPlane", far_clip)
                except Exception:
                    pass

        # --- Hide grid ---
        if model_panel:
            try:
                state["original_grid"] = cmds.modelEditor(
                    model_panel, query=True, grid=True)
                cmds.modelEditor(model_panel, edit=True, grid=False)
            except Exception:
                pass

        # --- Clear selection ---
        state["original_sel"] = cmds.ls(selection=True)
        cmds.select(clear=True)

        # ============================================================
        # Tab-specific overrides (only when NOT raw playblast)
        # ============================================================
        if not raw_pb and model_panel:
            if active_tab == TAB_CAMERA_TRACK:
                self._enter_preview_ct(state, model_panel)
            elif active_tab in (TAB_MATCHMOVE, TAB_FACE_TRACK):
                self._enter_preview_mm_ft(state, active_tab, model_panel,
                                          camera)

            # --- Flat lighting (all tabs) ---
            try:
                state["original_flat_lighting"] = cmds.modelEditor(
                    model_panel, query=True, displayLights=True)
                cmds.modelEditor(
                    model_panel, edit=True, displayLights="flat")
            except Exception:
                pass

            # --- Backface culling (all tabs) ---
            original_culling = {}
            for mesh in (cmds.ls(type="mesh", long=True) or []):
                try:
                    original_culling[mesh] = cmds.getAttr(
                        mesh + ".backfaceCulling")
                    cmds.setAttr(mesh + ".backfaceCulling", 3)
                except Exception:
                    pass
            state["original_culling"] = original_culling

        # Set playblast colour management (persists in scene)
        if not raw_pb and not custom_vt:
            try:
                exporter = Exporter(self._log)
                exporter._ensure_playblast_raw_srgb()
            except Exception:
                pass

            # Set viewport view transform to Raw so the live preview
            # matches the playblast output.  The playblast pref only
            # applies during cmds.playblast(), not the live viewport.
            if model_panel:
                try:
                    state["original_viewTransform"] = cmds.modelEditor(
                        model_panel, query=True, viewTransformName=True)
                except Exception:
                    state["original_viewTransform"] = ""
                # Find the Raw transform name (reuse the same search
                # logic that _ensure_playblast_raw_srgb uses).
                vt_names = []
                try:
                    vt_names = (
                        cmds.colorManagementPrefs(
                            query=True, viewTransformNames=True) or [])
                except Exception:
                    pass
                raw_vt = None
                for n in vt_names:
                    if n == "Raw":
                        raw_vt = n
                        break
                if not raw_vt:
                    for n in vt_names:
                        if n.startswith("Raw"):
                            raw_vt = n
                            break
                if not raw_vt:
                    for n in vt_names:
                        if "raw" in n.lower():
                            raw_vt = n
                            break
                if raw_vt:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            viewTransformName=raw_vt)
                    except Exception:
                        pass

        cmds.refresh(force=True)

        self._preview_state = state

    def _enter_preview_ct(self, state, model_panel):
        """Apply Camera Track viewport overrides for preview."""
        wf_shader = cmds.checkBox(
            self.pb_wireframe_shader_cb, query=True, value=True)
        aa16 = cmds.checkBox(
            self.pb_aa16_cb, query=True, value=True)
        geo_roots = []
        for entry in self.ct_geo_fields:
            g = cmds.textFieldButtonGrp(
                entry["field"], query=True, text=True).strip()
            if g:
                geo_roots.append(g)

        if wf_shader and geo_roots:
            # Wireframe-on-shaded with useBackground shader
            state["original_display"] = cmds.modelEditor(
                model_panel, query=True, displayAppearance=True)
            cmds.modelEditor(
                model_panel, edit=True,
                displayAppearance="smoothShaded")
            state["original_ct_wos"] = cmds.modelEditor(
                model_panel, query=True, wireframeOnShaded=True)
            cmds.modelEditor(
                model_panel, edit=True, wireframeOnShaded=True)

            # Create useBackground shader
            bg_shader = cmds.shadingNode(
                "useBackground", asShader=True,
                name="mme_ctBgShader_mtl")
            bg_sg = cmds.sets(
                renderable=True, noSurfaceShader=True,
                empty=True, name="mme_ctBgShader_SG")
            cmds.connectAttr(
                "{}.outColor".format(bg_shader),
                "{}.surfaceShader".format(bg_sg),
                force=True)
            state["ct_bg_shader_nodes"] = [bg_shader, bg_sg]

            ct_meshes = []
            wf_geo_list = geo_roots if isinstance(
                geo_roots, list) else [geo_roots]
            for geo_node in wf_geo_list:
                if geo_node and cmds.objExists(geo_node):
                    descendants = cmds.listRelatives(
                        geo_node, allDescendents=True,
                        type="mesh", fullPath=True) or []
                    for m in descendants:
                        try:
                            if not cmds.getAttr(
                                    m + ".intermediateObject"):
                                ct_meshes.append(m)
                        except Exception:
                            pass
            ct_transforms = list(set(
                cmds.listRelatives(
                    ct_meshes, parent=True,
                    fullPath=True) or []
            )) if ct_meshes else []

            original_ct_shading = {}
            for mesh in ct_meshes:
                try:
                    sgs = cmds.listConnections(
                        mesh, type="shadingEngine") or []
                    if sgs:
                        original_ct_shading[mesh] = sgs[0]
                except Exception:
                    pass
            state["original_ct_shading"] = original_ct_shading

            if ct_transforms:
                cmds.select(ct_transforms, replace=True)
                cmds.hyperShade(assign=bg_shader)
                cmds.select(clear=True)
        else:
            # Default camera track: pure wireframe
            state["original_display"] = cmds.modelEditor(
                model_panel, query=True, displayAppearance=True)
            if state["original_display"] != "wireframe":
                cmds.modelEditor(
                    model_panel, edit=True,
                    displayAppearance="wireframe")

        # Anti-aliasing
        try:
            state["original_aa"] = cmds.getAttr(
                "hardwareRenderingGlobals.multiSampleEnable")
            cmds.setAttr(
                "hardwareRenderingGlobals.multiSampleEnable", True)
        except Exception:
            pass
        try:
            state["original_msaa_count"] = cmds.getAttr(
                "hardwareRenderingGlobals.multiSampleCount")
            cmds.setAttr(
                "hardwareRenderingGlobals.multiSampleCount",
                16 if aa16 else 8)
        except Exception:
            pass
        try:
            state["original_smooth_wire"] = cmds.modelEditor(
                model_panel, query=True, smoothWireframe=True)
            cmds.modelEditor(
                model_panel, edit=True, smoothWireframe=True)
        except Exception:
            pass

        # Ensure geo types visible
        original_editor_vis = {}
        for flag in ("polymeshes", "nurbsSurfaces", "subdivSurfaces"):
            try:
                original_editor_vis[flag] = cmds.modelEditor(
                    model_panel, query=True, **{flag: True})
                cmds.modelEditor(
                    model_panel, edit=True, **{flag: True})
            except Exception:
                pass
        state["original_editor_vis"] = original_editor_vis

    def _enter_preview_mm_ft(self, state, active_tab, model_panel,
                             camera):
        """Apply Matchmove / Face Track viewport overrides for preview.

        Preview uses a single-pass semi-transparent Lambert checker
        overlay (not the multi-pass composite pipeline used for export).
        This is intentional — preview is interactive and doesn't need
        the full composite; the checker gives a good enough
        approximation for viewport QC.
        """
        aa16 = cmds.checkBox(
            self.pb_aa16_cb, query=True, value=True)
        chk_scale = cmds.intSliderGrp(
            self.pb_checker_scale, query=True, value=True)
        chk_color = tuple(cmds.colorSliderGrp(
            self.pb_checker_color, query=True, rgbValue=True))
        chk_opacity = cmds.intSliderGrp(
            self.pb_checker_opacity, query=True, value=True)
        if active_tab == TAB_MATCHMOVE:
            geo_roots = []
            for pair in self.mm_rig_geo_pairs:
                g = cmds.textFieldButtonGrp(
                    pair["geo_field"], query=True, text=True).strip()
                if g:
                    geo_roots.append(g)
        else:  # TAB_FACE_TRACK
            geo_roots = []
            for entry in self.ft_face_mesh_entries:
                fm = cmds.textFieldButtonGrp(
                    entry["field"], query=True, text=True).strip()
                if fm:
                    geo_roots.append(fm)

        matchmove_geo = [
            g for g in geo_roots if g and cmds.objExists(g)]

        if not matchmove_geo:
            return

        # 1. Force display layers visible
        original_layer_vis = {}
        original_layer_playback = {}
        for layer in (cmds.ls(type="displayLayer") or []):
            if layer == "defaultLayer":
                continue
            try:
                original_layer_vis[layer] = cmds.getAttr(
                    layer + ".visibility")
                cmds.setAttr(layer + ".visibility", True)
            except Exception:
                pass
            try:
                original_layer_playback[layer] = cmds.getAttr(
                    layer + ".hideOnPlayback")
                cmds.setAttr(layer + ".hideOnPlayback", False)
            except Exception:
                pass
        state["original_layer_vis"] = original_layer_vis
        state["original_layer_playback"] = original_layer_playback

        # 2. Isolate select
        state["original_isolate_state"] = cmds.isolateSelect(
            model_panel, query=True, state=True)
        cmds.isolateSelect(model_panel, state=True)
        for geo_root in matchmove_geo:
            cmds.isolateSelect(
                model_panel, addDagObject=geo_root)
        if camera:
            try:
                cmds.isolateSelect(
                    model_panel, addDagObject=camera)
            except Exception:
                pass
            cam_shapes = cmds.listRelatives(
                camera, shapes=True, type="camera") or []
            for cs in cam_shapes:
                img_planes = cmds.listConnections(
                    cs + ".imagePlane",
                    type="imagePlane") or []
                for ip in img_planes:
                    try:
                        cmds.isolateSelect(
                            model_panel, addDagObject=ip)
                    except Exception:
                        pass

        # 3. Enable image planes
        state["original_image_plane"] = cmds.modelEditor(
            model_panel, query=True, imagePlane=True)
        cmds.modelEditor(model_panel, edit=True, imagePlane=True)

        # 3b. NURBS curves — hide except QC_head_GRP
        state["original_nurbs_curves"] = cmds.modelEditor(
            model_panel, query=True, nurbsCurves=True)
        if (cmds.objExists("QC_head_GRP")
                and cmds.listRelatives(
                    "QC_head_GRP", allDescendents=True,
                    type="nurbsCurve")):
            cmds.modelEditor(
                model_panel, edit=True, nurbsCurves=True)
            cmds.isolateSelect(
                model_panel, addDagObject="QC_head_GRP")
        else:
            cmds.modelEditor(
                model_panel, edit=True, nurbsCurves=False)

        # 4. Smooth shaded, no wireframe overlay
        state["original_mm_display"] = cmds.modelEditor(
            model_panel, query=True, displayAppearance=True)
        cmds.modelEditor(
            model_panel, edit=True,
            displayAppearance="smoothShaded")
        state["original_mm_wos"] = cmds.modelEditor(
            model_panel, query=True, wireframeOnShaded=True)
        cmds.modelEditor(
            model_panel, edit=True, wireframeOnShaded=False)

        # 5. Smooth wireframe + MSAA + motion blur
        try:
            state["original_mm_smooth_wire"] = cmds.modelEditor(
                model_panel, query=True, smoothWireframe=True)
            cmds.modelEditor(
                model_panel, edit=True, smoothWireframe=True)
        except Exception:
            pass
        try:
            state["original_mm_aa"] = cmds.getAttr(
                "hardwareRenderingGlobals.multiSampleEnable")
            cmds.setAttr(
                "hardwareRenderingGlobals.multiSampleEnable", True)
        except Exception:
            pass
        try:
            state["original_mm_msaa_count"] = cmds.getAttr(
                "hardwareRenderingGlobals.multiSampleCount")
            cmds.setAttr(
                "hardwareRenderingGlobals.multiSampleCount",
                16 if aa16 else 8)
        except Exception:
            pass
        try:
            state["original_mm_motion_blur"] = cmds.getAttr(
                "hardwareRenderingGlobals.motionBlurEnable")
            cmds.setAttr(
                "hardwareRenderingGlobals.motionBlurEnable", True)
        except Exception:
            pass

        # 6. UV checker overlay
        checker_nodes = []
        original_shading = {}
        try:
            mm_meshes = []
            for geo_root in matchmove_geo:
                descendants = cmds.listRelatives(
                    geo_root, allDescendents=True,
                    type="mesh", fullPath=True) or []
                for m in descendants:
                    try:
                        if not cmds.getAttr(
                                m + ".intermediateObject"):
                            mm_meshes.append(m)
                    except Exception:
                        pass
            mm_transforms = list(set(
                cmds.listRelatives(
                    mm_meshes, parent=True,
                    fullPath=True) or []
            )) if mm_meshes else []

            for mesh in mm_meshes:
                try:
                    sgs = cmds.listConnections(
                        mesh, type="shadingEngine") or []
                    if sgs:
                        original_shading[mesh] = sgs[0]
                except Exception:
                    pass

            # Create checker shader network
            chk_lambert = cmds.shadingNode(
                "lambert", asShader=True,
                name="mme_uvChecker_mtl")
            checker_nodes.append(chk_lambert)
            transp = 1.0 - (chk_opacity / 100.0)
            cmds.setAttr(
                "{}.transparency".format(chk_lambert),
                transp, transp, transp, type="double3")

            chk_sg = cmds.sets(
                renderable=True, noSurfaceShader=True,
                empty=True, name="mme_uvChecker_SG")
            checker_nodes.append(chk_sg)
            cmds.connectAttr(
                "{}.outColor".format(chk_lambert),
                "{}.surfaceShader".format(chk_sg),
                force=True)

            chk_color = chk_color or (0.75, 0.75, 0.75)
            chk_color2 = (
                chk_color[0] * 0.33,
                chk_color[1] * 0.33,
                chk_color[2] * 0.33,
            )
            chk_tex = cmds.shadingNode(
                "checker", asTexture=True,
                name="mme_uvChecker_tex")
            checker_nodes.append(chk_tex)
            cmds.setAttr(
                "{}.color1".format(chk_tex),
                chk_color[0], chk_color[1], chk_color[2],
                type="double3")
            cmds.setAttr(
                "{}.color2".format(chk_tex),
                chk_color2[0], chk_color2[1], chk_color2[2],
                type="double3")

            chk_place = cmds.shadingNode(
                "place2dTexture", asUtility=True,
                name="mme_uvChecker_place")
            checker_nodes.append(chk_place)
            repeat = max(1, 33 - chk_scale)
            cmds.setAttr("{}.repeatU".format(chk_place), repeat)
            cmds.setAttr("{}.repeatV".format(chk_place), repeat)

            for attr in (
                "coverage", "translateFrame", "rotateFrame",
                "mirrorU", "mirrorV", "stagger", "wrapU",
                "wrapV", "repeatUV", "offset", "rotateUV",
                "noiseUV", "vertexUvOne", "vertexUvTwo",
                "vertexUvThree", "vertexCameraOne",
            ):
                if (cmds.attributeQuery(
                        attr, node=chk_place, exists=True)
                        and cmds.attributeQuery(
                            attr, node=chk_tex, exists=True)):
                    cmds.connectAttr(
                        "{}.{}".format(chk_place, attr),
                        "{}.{}".format(chk_tex, attr),
                        force=True)
            cmds.connectAttr(
                "{}.outUV".format(chk_place),
                "{}.uvCoord".format(chk_tex),
                force=True)
            cmds.connectAttr(
                "{}.outUvFilterSize".format(chk_place),
                "{}.uvFilterSize".format(chk_tex),
                force=True)
            cmds.connectAttr(
                "{}.outColor".format(chk_tex),
                "{}.color".format(chk_lambert),
                force=True)

            if mm_transforms:
                cmds.select(mm_transforms, replace=True)
                cmds.hyperShade(assign=chk_lambert)
                cmds.select(clear=True)

            state["original_use_default_mtl"] = cmds.modelEditor(
                model_panel, query=True, useDefaultMaterial=True)
            cmds.modelEditor(
                model_panel, edit=True, useDefaultMaterial=False)

            state["original_display_textures"] = cmds.modelEditor(
                model_panel, query=True, displayTextures=True)
            state["original_display_lights"] = cmds.modelEditor(
                model_panel, query=True, displayLights=True)
            cmds.modelEditor(
                model_panel, edit=True,
                displayTextures=True,
                displayLights="default")

            cmds.ogs(reset=True)
            cmds.currentTime(cmds.currentTime(query=True))
            cmds.refresh(force=True)
        except Exception:
            pass

        state["checker_nodes"] = checker_nodes
        state["original_shading"] = original_shading

    def _exit_preview_mode(self):
        """Restore all viewport settings saved in _preview_state."""
        state = self._preview_state
        if not state:
            self._preview_active = False
            return

        model_panel = state.get("model_panel")
        camera = state.get("camera")
        active_tab = state.get("tab")
        raw_pb = state.get("raw_playblast", False)

        if not raw_pb and model_panel:
            # --- Restore Camera Track overrides ---
            if active_tab == TAB_CAMERA_TRACK:
                for flag, val in state.get(
                        "original_editor_vis", {}).items():
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True, **{flag: val})
                    except Exception:
                        pass
                if "original_aa" in state:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals"
                            ".multiSampleEnable",
                            state["original_aa"])
                    except Exception:
                        pass
                if "original_msaa_count" in state:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals"
                            ".multiSampleCount",
                            state["original_msaa_count"])
                    except Exception:
                        pass
                if "original_smooth_wire" in state:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            smoothWireframe=state[
                                "original_smooth_wire"])
                    except Exception:
                        pass
                if "original_display" in state:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayAppearance=state[
                                "original_display"])
                    except Exception:
                        pass
                if "original_ct_wos" in state:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            wireframeOnShaded=state[
                                "original_ct_wos"])
                    except Exception:
                        pass
                # Restore useBackground shader assignments
                for mesh, sg in state.get(
                        "original_ct_shading", {}).items():
                    try:
                        if (cmds.objExists(mesh)
                                and cmds.objExists(sg)):
                            cmds.sets(
                                mesh, edit=True, forceElement=sg)
                    except Exception:
                        pass
                for node in state.get("ct_bg_shader_nodes", []):
                    try:
                        if cmds.objExists(node):
                            cmds.delete(node)
                    except Exception:
                        pass

            # --- Restore Matchmove / Face Track overrides ---
            elif active_tab in (TAB_MATCHMOVE, TAB_FACE_TRACK):
                # Restore shading before deleting checker nodes
                for mesh, sg in state.get(
                        "original_shading", {}).items():
                    try:
                        if (cmds.objExists(mesh)
                                and cmds.objExists(sg)):
                            cmds.sets(
                                mesh, edit=True, forceElement=sg)
                    except Exception:
                        pass
                if "original_display_textures" in state:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayTextures=state[
                                "original_display_textures"])
                    except Exception:
                        pass
                if "original_display_lights" in state:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayLights=state[
                                "original_display_lights"])
                    except Exception:
                        pass
                if "original_use_default_mtl" in state:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            useDefaultMaterial=state[
                                "original_use_default_mtl"])
                    except Exception:
                        pass
                if "original_image_plane" in state:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            imagePlane=state[
                                "original_image_plane"])
                    except Exception:
                        pass
                if "original_nurbs_curves" in state:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            nurbsCurves=state[
                                "original_nurbs_curves"])
                    except Exception:
                        pass
                for node in state.get("checker_nodes", []):
                    try:
                        if cmds.objExists(node):
                            cmds.delete(node)
                    except Exception:
                        pass
                if "original_mm_display" in state:
                    cmds.modelEditor(
                        model_panel, edit=True,
                        displayAppearance=state[
                            "original_mm_display"])
                if "original_mm_wos" in state:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            wireframeOnShaded=state[
                                "original_mm_wos"])
                    except Exception:
                        pass
                if "original_mm_smooth_wire" in state:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            smoothWireframe=state[
                                "original_mm_smooth_wire"])
                    except Exception:
                        pass
                if "original_mm_aa" in state:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals"
                            ".multiSampleEnable",
                            state["original_mm_aa"])
                    except Exception:
                        pass
                if "original_mm_msaa_count" in state:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals"
                            ".multiSampleCount",
                            state["original_mm_msaa_count"])
                    except Exception:
                        pass
                if "original_mm_motion_blur" in state:
                    try:
                        cmds.setAttr(
                            "hardwareRenderingGlobals"
                            ".motionBlurEnable",
                            state["original_mm_motion_blur"])
                    except Exception:
                        pass
                # Restore isolate select
                try:
                    cmds.isolateSelect(
                        model_panel,
                        state=state.get(
                            "original_isolate_state", False))
                except Exception:
                    pass
                # Restore display layers
                for layer, val in state.get(
                        "original_layer_vis", {}).items():
                    try:
                        if cmds.objExists(layer):
                            cmds.setAttr(
                                layer + ".visibility", val)
                    except Exception:
                        pass
                for layer, val in state.get(
                        "original_layer_playback", {}).items():
                    try:
                        if cmds.objExists(layer):
                            cmds.setAttr(
                                layer + ".hideOnPlayback", val)
                    except Exception:
                        pass

            # --- Shared restores ---
            if "original_flat_lighting" in state:
                try:
                    cmds.modelEditor(
                        model_panel, edit=True,
                        displayLights=state[
                            "original_flat_lighting"])
                except Exception:
                    pass
            for mesh, val in state.get(
                    "original_culling", {}).items():
                try:
                    if cmds.objExists(mesh):
                        cmds.setAttr(
                            mesh + ".backfaceCulling", val)
                except Exception:
                    pass
            # Restore viewport view transform
            if "original_viewTransform" in state:
                try:
                    cmds.modelEditor(
                        model_panel, edit=True,
                        viewTransformName=state[
                            "original_viewTransform"])
                except Exception:
                    pass

        # --- Always restore camera, pan/zoom, far clip, grid, sel ---
        if camera:
            cam_shapes = cmds.listRelatives(
                camera, shapes=True, type="camera") or []
            if cam_shapes:
                cs = cam_shapes[0]
                if "original_pan_zoom" in state:
                    try:
                        cmds.setAttr(
                            cs + ".panZoomEnabled",
                            state["original_pan_zoom"])
                    except Exception:
                        pass
                if "original_far_clip" in state:
                    try:
                        cmds.setAttr(
                            cs + ".farClipPlane",
                            state["original_far_clip"])
                    except Exception:
                        pass
        if "original_grid" in state and model_panel:
            try:
                cmds.modelEditor(
                    model_panel, edit=True,
                    grid=state["original_grid"])
            except Exception:
                pass
        if "original_cam" in state and model_panel:
            cmds.lookThru(model_panel, state["original_cam"])
        original_sel = state.get("original_sel")
        if original_sel:
            try:
                cmds.select(original_sel, replace=True)
            except Exception:
                pass

        cmds.refresh(force=True)

        # --- Reset state and buttons ---
        self._preview_state = {}
        self._preview_active = False
        for btn in self._preview_buttons:
            try:
                cmds.button(btn, edit=True,
                            label="Preview Playblast",
                            backgroundColor=[0.365, 0.365, 0.365])
            except Exception:
                pass
        for hint in self._preview_hints:
            try:
                cmds.text(hint, edit=True, visible=False)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Export Pipelines
    # ------------------------------------------------------------------

    def _export_camera_track(self):
        """Export pipeline for Camera Track tab."""
        errors, warnings = self._validate_camera_track()
        if errors:
            for e in errors:
                self._log(e)
            cmds.confirmDialog(
                title="Export Errors",
                message="Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(errors)),
                button=["OK"],
            )
            return

        if warnings:
            result = cmds.confirmDialog(
                title="Warnings",
                message="Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(warnings)),
                button=["Continue", "Cancel"],
                defaultButton="Continue",
                cancelButton="Cancel",
                dismissString="Cancel",
            )
            if result == "Cancel":
                self._log("Export cancelled by user.")
                return

        original_sel = cmds.ls(selection=True)

        # Gather settings
        export_root = cmds.textFieldButtonGrp(
            self.export_root_field, query=True, text=True
        ).strip()
        camera = cmds.textFieldButtonGrp(
            self.ct_camera_field, query=True, text=True
        ).strip()
        geo_roots = []
        for entry in self.ct_geo_fields:
            g = cmds.textFieldButtonGrp(
                entry["field"], query=True, text=True
            ).strip()
            if g:
                geo_roots.append(g)
        do_ma = cmds.checkBox(self.ct_ma_checkbox, query=True, value=True)
        do_jsx = cmds.checkBox(self.ct_jsx_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.ct_fbx_checkbox, query=True, value=True)
        do_abc = cmds.checkBox(self.ct_abc_checkbox, query=True, value=True)
        do_mov = cmds.checkBox(self.ct_mov_checkbox, query=True, value=True)
        start_frame = cmds.intField(
            self.start_frame_field, query=True, value=True
        )
        end_frame = cmds.intField(
            self.end_frame_field, query=True, value=True
        )

        # Read version from UI field
        scene_short = cmds.file(
            query=True, sceneName=True, shortName=True
        )
        version_str = cmds.textFieldGrp(
            self.version_field, query=True, text=True).strip()
        if not version_str:
            version_str = "v01"
        scene_base = VersionParser.get_scene_base_name(scene_short)

        # Resolve versioned directories (rename older version folders)
        FolderManager.resolve_versioned_dir(
            export_root, scene_base, version_str
        )
        main_dir = os.path.join(
            export_root,
            "{}_track_{}".format(scene_base, version_str),
        )
        FolderManager.resolve_ae_dir(main_dir, scene_base, version_str)

        self._log("Exporting to: {}".format(main_dir))

        exporter = Exporter(self._log)
        results = {}
        all_paths = {}

        # Progress bar — JSX counts as 2 steps (setup + timeline scrub)
        total_formats = sum([do_ma, do_fbx, do_abc, do_mov])
        if do_jsx:
            total_formats += 2
        self._reset_progress(total_formats)

        # Rename camera to cam_main for all exports
        renamed_cam = None
        original_cam_name = camera
        baked_abc_cam = False
        try:
            if camera:
                if camera == "cam_main" and cmds.objExists(camera):
                    # Already named correctly — no rename needed
                    pass
                elif cmds.objExists(camera):
                    renamed_cam = cmds.rename(camera, "cam_main")
                    camera = renamed_cam
                elif cmds.objExists("cam_main"):
                    # Previous run may have renamed without restoring
                    renamed_cam = "cam_main"
                    camera = "cam_main"
                else:
                    self._log(
                        "Camera not found. See Script Editor.")
                    camera = None

            # Detect Alembic-driven camera and bake before exports
            if camera and cmds.objExists(camera):
                cam_shapes = cmds.listRelatives(
                    camera, shapes=True, type="camera") or []
                abc_nodes = set()
                # Check transform TRS channels
                for attr in ("tx", "ty", "tz", "rx", "ry", "rz",
                             "sx", "sy", "sz"):
                    conns = cmds.listConnections(
                        "{}.{}".format(camera, attr),
                        source=True, destination=False) or []
                    for c in conns:
                        if cmds.nodeType(c) == "AlembicNode":
                            abc_nodes.add(c)
                # Check camera shape focalLength
                for shp in cam_shapes:
                    conns = cmds.listConnections(
                        "{}.focalLength".format(shp),
                        source=True, destination=False) or []
                    for c in conns:
                        if cmds.nodeType(c) == "AlembicNode":
                            abc_nodes.add(c)
                if abc_nodes:
                    self._log("Baking Alembic camera...")
                    cmds.undoInfo(openChunk=True)
                    baked_abc_cam = True
                    trs = ["tx", "ty", "tz", "rx", "ry", "rz",
                           "sx", "sy", "sz"]
                    # Unlock TRS channels
                    for a in trs:
                        try:
                            cmds.setAttr(
                                "{}.{}".format(camera, a),
                                lock=False, keyable=True,
                                channelBox=True)
                        except Exception:
                            pass
                    # Bake transform channels
                    cmds.bakeResults(
                        camera,
                        t=(int(start_frame), int(end_frame)),
                        at=trs,
                        simulation=True,
                        preserveOutsideKeys=True,
                        minimizeRotation=True,
                    )
                    # Bake focal length on camera shape
                    for shp in cam_shapes:
                        try:
                            cmds.setAttr(
                                "{}.focalLength".format(shp),
                                lock=False, keyable=True)
                        except Exception:
                            pass
                        cmds.bakeResults(
                            shp,
                            t=(int(start_frame), int(end_frame)),
                            at=["focalLength"],
                            simulation=True,
                            preserveOutsideKeys=True,
                        )
                    # Disconnect Alembic sources (keep baked animCurves)
                    all_plugs = ["{}.{}".format(camera, a) for a in trs]
                    for shp in cam_shapes:
                        all_plugs.append(
                            "{}.focalLength".format(shp))
                    for plug in all_plugs:
                        conns = cmds.listConnections(
                            plug, source=True, destination=False,
                            plugs=True,
                            skipConversionNodes=True) or []
                        for src_plug in conns:
                            src_node = src_plug.split(".")[0]
                            if cmds.nodeType(src_node).startswith(
                                    "animCurve"):
                                continue
                            try:
                                cmds.disconnectAttr(src_plug, plug)
                            except Exception:
                                pass
                    sys.stderr.write(
                        "[ExportGenie] Baked Alembic camera: {} "
                        "({} AlembicNode(s) disconnected).\n".format(
                            camera, len(abc_nodes)))

            # JSX + OBJ export
            if do_jsx:
                geo_children = []
                for gr in geo_roots:
                    children = cmds.listRelatives(
                        gr, children=True, type="transform",
                        fullPath=True,
                    ) or []
                    if children:
                        geo_children.extend(children)
                    else:
                        gr_long = cmds.ls(gr, long=True)
                        geo_children.extend(
                            gr_long if gr_long else [gr])
                # Exclude camera, chisels, and nulls from OBJ paths
                # (nulls/locators are handled separately inside export_jsx)
                if camera:
                    geo_children = [
                        c for c in geo_children
                        if not Exporter._is_descendant_of(camera, c)
                    ]
                geo_children = [
                    c for c in geo_children
                    if "chisels" not in c.lower()
                    and "nulls" not in c.lower()
                ]

                ae_paths = FolderManager.build_ae_export_paths(
                    export_root, scene_base, version_str, geo_children
                )
                FolderManager.ensure_ae_directories(ae_paths)
                all_paths["jsx"] = ae_paths["jsx"]
                self._advance_progress()  # step 1: setup complete

                # JSX export uses the first geo root as the primary group
                jsx_geo_root = geo_roots[0] if geo_roots else None
                results["jsx"] = exporter.export_jsx(
                    ae_paths["jsx"], ae_paths["obj"], camera, jsx_geo_root,
                    start_frame, end_frame
                )
                self._log_result("JSX + OBJ", results["jsx"])
                self._advance_progress()  # step 2: JSX scrub complete

            if do_ma:
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str, tag="cam"
                )
                FolderManager.ensure_directories({"ma": paths["ma"]})
                all_paths["ma"] = paths["ma"]
                results["ma"] = exporter.export_ma(
                    paths["ma"], camera, geo_roots, [], [],
                    start_frame=start_frame, end_frame=end_frame,
                )
                self._log_result("MA", results["ma"])
                self._advance_progress()

            if do_fbx:
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str, tag="cam"
                )
                FolderManager.ensure_directories({"fbx": paths["fbx"]})
                all_paths["fbx"] = paths["fbx"]
                results["fbx"] = exporter.export_fbx(
                    paths["fbx"], camera, geo_roots, [], [],
                    start_frame, end_frame
                )
                self._log_result("FBX", results["fbx"])
                self._advance_progress()

            if do_abc:
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str, tag="cam"
                )
                FolderManager.ensure_directories({"abc": paths["abc"]})
                all_paths["abc"] = paths["abc"]
                results["abc"] = exporter.export_abc(
                    paths["abc"], camera, geo_roots, [],
                    start_frame, end_frame
                )
                self._log_result("ABC", results["abc"])
                self._advance_progress()

            if do_mov:
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str, tag="cam"
                )
                fmt_choice = cmds.optionMenu(
                    self.ct_mov_format_menu, query=True, value=True)
                png_mode = "PNG" in fmt_choice
                mp4_mode = ".mp4" in fmt_choice
                if mp4_mode and not Exporter._find_ffmpeg():
                    self._log(
                        "Playblast skipped — ffmpeg not found.")
                    results["mov"] = False
                else:
                    if mp4_mode:
                        pb_path = paths["mp4_tmp_file"]
                        if not os.path.exists(paths["mp4_tmp_dir"]):
                            os.makedirs(paths["mp4_tmp_dir"])
                        all_paths["mov"] = paths["mp4"]
                    elif png_mode:
                        pb_path = paths["png_file"]
                        if not os.path.exists(paths["png_dir"]):
                            os.makedirs(paths["png_dir"])
                        all_paths["mov"] = paths["png_dir"]
                    else:
                        pb_path = paths["mov"]
                        FolderManager.ensure_directories(
                            {"mov": paths["mov"]})
                        all_paths["mov"] = paths["mov"]
                    self._log("Preparing playblast...")
                    raw_pb = cmds.checkBox(
                        self.pb_raw_playblast_cb, query=True,
                        value=True)
                    custom_vt = cmds.checkBox(
                        self.pb_custom_vt_cb, query=True,
                        value=True)
                    wf_shader = cmds.checkBox(
                        self.pb_wireframe_shader_cb, query=True,
                        value=True)
                    aa16 = cmds.checkBox(
                        self.pb_aa16_cb, query=True, value=True)
                    far_clip = cmds.intSliderGrp(
                        self.pb_far_clip, query=True, value=True)
                    show_hud = cmds.checkBox(
                        self.pb_hud_overlay_cb, query=True,
                        value=True)
                    results["mov"] = exporter.export_playblast(
                        pb_path, camera, start_frame, end_frame,
                        camera_track_mode=True,
                        raw_playblast=raw_pb,
                        render_raw_srgb=not custom_vt,
                        wireframe_shader=wf_shader,
                        wireframe_shader_geo=geo_roots,
                        msaa_16=aa16,
                        far_clip=far_clip,
                        png_mode=png_mode,
                        mp4_mode=mp4_mode,
                        mp4_output=paths.get("mp4"),
                        show_hud=show_hud,
                    )
                    self._log_result("Playblast", results["mov"])
                self._advance_progress()
        finally:
            # Undo Alembic camera bake (restores original connections)
            if baked_abc_cam:
                try:
                    cmds.undoInfo(closeChunk=True)
                    cmds.undo()
                except Exception:
                    self._log(
                        "Undo camera bake failed. See Script Editor.")
            # Restore original camera name
            if renamed_cam and cmds.objExists(renamed_cam):
                cmds.rename(renamed_cam, original_cam_name)

        self._finish_export(results, all_paths, original_sel)

    def _export_matchmove(self):
        """Export pipeline for Matchmove tab (identical to v1.0 behavior)."""
        errors, warnings = self._validate_matchmove()
        if errors:
            for e in errors:
                self._log(e)
            cmds.confirmDialog(
                title="Export Errors",
                message="Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(errors)),
                button=["OK"],
            )
            return

        if warnings:
            result = cmds.confirmDialog(
                title="Warnings",
                message="Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(warnings)),
                button=["Continue", "Cancel"],
                defaultButton="Continue",
                cancelButton="Cancel",
                dismissString="Cancel",
            )
            if result == "Cancel":
                self._log("Export cancelled by user.")
                return

        original_sel = cmds.ls(selection=True)

        # Gather settings
        export_root = cmds.textFieldButtonGrp(
            self.export_root_field, query=True, text=True
        ).strip()
        camera = cmds.textFieldButtonGrp(
            self.mm_camera_field, query=True, text=True
        ).strip()
        proxy_geos = []
        for entry in self.mm_static_geo_fields:
            pg = cmds.textFieldButtonGrp(
                entry["field"], query=True, text=True
            ).strip()
            if pg:
                proxy_geos.append(pg)
        rig_roots = []
        geo_roots = []
        for pair in self.mm_rig_geo_pairs:
            r = cmds.textFieldButtonGrp(
                pair["rig_field"], query=True, text=True
            ).strip()
            g = cmds.textFieldButtonGrp(
                pair["geo_field"], query=True, text=True
            ).strip()
            if r:
                rig_roots.append(r)
            if g:
                geo_roots.append(g)
        do_ma = cmds.checkBox(self.mm_ma_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.mm_fbx_checkbox, query=True, value=True)
        do_abc = cmds.checkBox(self.mm_abc_checkbox, query=True, value=True)
        do_mov = cmds.checkBox(self.mm_mov_checkbox, query=True, value=True)
        start_frame = cmds.intField(
            self.start_frame_field, query=True, value=True
        )
        end_frame = cmds.intField(
            self.end_frame_field, query=True, value=True
        )

        # T-pose handling: FBX and ABC include T-pose frame in their
        # range.  The .ma export and QC playblast keep the original
        # timeline range (T-pose exists outside the range in .ma).
        tpose_start = start_frame
        if cmds.checkBox(self.tpose_checkbox, query=True, value=True):
            tpose_frame = cmds.intField(
                self.tpose_frame_field, query=True, value=True
            )
            tpose_start = min(start_frame, tpose_frame)

        # Read version from UI field
        scene_short = cmds.file(
            query=True, sceneName=True, shortName=True
        )
        version_str = cmds.textFieldGrp(
            self.version_field, query=True, text=True).strip()
        if not version_str:
            version_str = "v01"
        scene_base = VersionParser.get_scene_base_name(scene_short)

        # Resolve versioned directories (rename older version folders)
        FolderManager.resolve_versioned_dir(
            export_root, scene_base, version_str
        )

        # Build paths and create directories (exclude PNG and MP4 temp
        # dirs — those are created on demand only when that format is selected)
        paths = FolderManager.build_export_paths(
            export_root, scene_base, version_str, tag="charMM"
        )
        FolderManager.ensure_directories(
            {k: v for k, v in paths.items()
             if k not in ("png_dir", "png_file",
                          "mp4_tmp_dir", "mp4_tmp_file",
                          "composite_tmp", "composite_plate",
                          "composite_color", "composite_matte")})

        dir_path = os.path.dirname(paths.get("ma", paths.get("fbx", "")))
        self._log("Exporting to: {}".format(dir_path))

        exporter = Exporter(self._log)
        results = {}

        # Progress bar
        total_formats = sum([do_ma, do_fbx, do_abc, do_mov])
        self._reset_progress(total_formats)

        # Rename camera to cam_main for all exports
        renamed_cam = None
        original_cam_name = camera
        try:
            if camera:
                if camera == "cam_main" and cmds.objExists(camera):
                    # Already named correctly — no rename needed
                    pass
                elif cmds.objExists(camera):
                    renamed_cam = cmds.rename(camera, "cam_main")
                    camera = renamed_cam
                elif cmds.objExists("cam_main"):
                    renamed_cam = "cam_main"
                    camera = "cam_main"
                else:
                    self._log(
                        "Camera not found. See Script Editor.")
                    camera = None

            # Unlock any locked locators in the export groups so that
            # FBX/ABC exporters can bake and export their transforms.
            _all_export_roots = geo_roots + rig_roots + proxy_geos
            if camera and cmds.objExists(camera):
                _all_export_roots.append(camera)
            _lock_attrs = [
                "tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
            for root in _all_export_roots:
                if not root or not cmds.objExists(root):
                    continue
                descendants = cmds.listRelatives(
                    root, allDescendents=True, fullPath=True) or []
                all_nodes = (cmds.ls(root, long=True) or []) + descendants
                for node in all_nodes:
                    loc_shapes = cmds.listRelatives(
                        node, shapes=True, type="locator") or []
                    if not loc_shapes:
                        continue
                    for attr in _lock_attrs:
                        plug = "{}.{}".format(node, attr)
                        try:
                            if cmds.getAttr(plug, lock=True):
                                cmds.setAttr(plug, lock=False)
                        except Exception:
                            pass

            if do_ma:
                results["ma"] = exporter.export_ma(
                    paths["ma"], camera, geo_roots, rig_roots, proxy_geos,
                    start_frame=start_frame, end_frame=end_frame,
                )
                self._log_result("MA", results["ma"])
                self._advance_progress()

            if do_fbx:
                self._log("Preparing FBX export...")
                cmds.undoInfo(openChunk=True)
                base_meshes = []
                target_groups = []
                try:
                    # Detect vertex-animated meshes before prep
                    # (Alembic connections must be intact for sampling)
                    vertex_anim_set = exporter.detect_vertex_anim_meshes(
                        geo_roots, tpose_start, end_frame)
                    has_vertex_anim = bool(vertex_anim_set)
                    if has_vertex_anim:
                        sys.stderr.write(
                            "[ExportGenie] Detected {} vertex-animated "
                            "mesh(es) in Mesh Group.\n".format(
                                len(vertex_anim_set)))

                    # Standard UE5 prep — skips vertex-anim meshes
                    # in Steps 4 (history) and 5 (freeze transforms)
                    exporter.prep_for_ue5_fbx_export(
                        geo_roots, rig_roots, tpose_start, end_frame,
                        camera=camera,
                        skip_mesh_xforms=vertex_anim_set)

                    # Namespace stripping in prep may have renamed nodes.
                    # Resolve to long (unique) names so select succeeds.
                    def _resolve_name(name):
                        """Return a unique DAG path after namespace strip."""
                        if not name:
                            return name
                        long_names = cmds.ls(name, long=True)
                        if long_names:
                            return long_names[0]
                        # Name gone — try without namespace prefix
                        short = name.rsplit(":", 1)[-1]
                        long_names = cmds.ls(short, long=True)
                        if len(long_names) == 1:
                            return long_names[0]
                        # Multiple matches — find by matching the
                        # hierarchy tail (strip namespaces from each
                        # segment of the original path)
                        if long_names:
                            stripped_tail = "/".join(
                                seg.rsplit(":", 1)[-1]
                                for seg in name.split("|") if seg)
                            for ln in long_names:
                                ln_tail = "/".join(
                                    seg for seg in ln.split("|") if seg)
                                if ln_tail.endswith(stripped_tail):
                                    return ln
                            return long_names[0]
                        return name

                    # Convert vertex-animated meshes to blendshapes
                    # (after prep so namespaces are stripped, but
                    # Alembic connections are still intact on skipped
                    # meshes)
                    if has_vertex_anim:
                        self._log("Converting vertex animation...")
                        for old_long in list(vertex_anim_set):
                            resolved = _resolve_name(old_long)
                            conv = exporter.convert_abc_to_blendshape(
                                resolved, tpose_start, end_frame)
                            base_meshes.append(conv["base_mesh"])
                            if conv.get("targets_group"):
                                target_groups.append(conv["targets_group"])

                    fbx_geo = [_resolve_name(g) for g in geo_roots]
                    fbx_rigs = [_resolve_name(r) for r in rig_roots]
                    fbx_proxies = [_resolve_name(p) for p in proxy_geos]
                    fbx_cam = _resolve_name(camera) if camera else camera
                    results["fbx"] = exporter.export_fbx(
                        paths["fbx"], fbx_cam, fbx_geo, fbx_rigs,
                        fbx_proxies, tpose_start, end_frame,
                        export_input_connections=has_vertex_anim,
                    )
                except Exception as exc:
                    self._log(
                        "FBX export failed. See Script Editor.")
                    sys.stderr.write(
                        "[ExportGenie] FBX error: {}\n".format(exc))
                    results["fbx"] = False
                finally:
                    cmds.undoInfo(closeChunk=True)
                    try:
                        cmds.undo()
                        self._log("Scene restored.")
                    except Exception:
                        self._log(
                            "Undo failed. See Script Editor.")
                    # Safety net: delete any blendshape artifacts
                    # that survived the undo
                    for bm in base_meshes:
                        if cmds.objExists(bm):
                            try:
                                cmds.delete(bm)
                            except Exception:
                                pass
                    for tg in target_groups:
                        if cmds.objExists(tg):
                            try:
                                cmds.delete(tg)
                            except Exception:
                                pass
                self._log_result("FBX", results.get("fbx", False))
                self._advance_progress()

            if do_abc:
                results["abc"] = exporter.export_abc(
                    paths["abc"], camera, geo_roots, proxy_geos,
                    tpose_start, end_frame
                )
                self._log_result("ABC", results["abc"])
                self._advance_progress()

            if do_mov:
                fmt_choice = cmds.optionMenu(
                    self.mm_mov_format_menu, query=True, value=True)
                png_mode = "PNG" in fmt_choice
                mp4_mode = ".mp4" in fmt_choice
                if mp4_mode and not Exporter._find_ffmpeg():
                    self._log(
                        "Playblast skipped — ffmpeg not found.")
                    results["mov"] = False
                else:
                    if mp4_mode:
                        pb_path = paths["mp4_tmp_file"]
                        if not os.path.exists(paths["mp4_tmp_dir"]):
                            os.makedirs(paths["mp4_tmp_dir"])
                    elif png_mode:
                        pb_path = paths["png_file"]
                        if not os.path.exists(paths["png_dir"]):
                            os.makedirs(paths["png_dir"])
                    else:
                        pb_path = paths["mov"]
                    self._log("Preparing playblast...")
                    raw_pb = cmds.checkBox(
                        self.pb_raw_playblast_cb, query=True,
                        value=True)
                    custom_vt = cmds.checkBox(
                        self.pb_custom_vt_cb, query=True,
                        value=True)
                    chk_scale = cmds.intSliderGrp(
                        self.pb_checker_scale, query=True, value=True)
                    chk_color = tuple(cmds.colorSliderGrp(
                        self.pb_checker_color, query=True,
                        rgbValue=True))
                    chk_opacity = cmds.intSliderGrp(
                        self.pb_checker_opacity, query=True,
                        value=True)
                    aa16 = cmds.checkBox(
                        self.pb_aa16_cb, query=True, value=True)
                    far_clip = cmds.intSliderGrp(
                        self.pb_far_clip, query=True, value=True)
                    show_hud = cmds.checkBox(
                        self.pb_hud_overlay_cb, query=True,
                        value=True)
                    results["mov"] = exporter.export_playblast(
                        pb_path, camera, start_frame, end_frame,
                        matchmove_geo=geo_roots,
                        checker_scale=chk_scale,
                        checker_color=chk_color,
                        checker_opacity=chk_opacity,
                        raw_playblast=raw_pb,
                        render_raw_srgb=not custom_vt,
                        msaa_16=aa16,
                        far_clip=far_clip,
                        png_mode=png_mode,
                        mp4_mode=mp4_mode,
                        mp4_output=paths.get("mp4"),
                        show_hud=show_hud,
                        composite_plate_path=paths.get(
                            "composite_plate"),
                        composite_color_path=paths.get(
                            "composite_color"),
                        composite_matte_path=paths.get(
                            "composite_matte"),
                        composite_tmp_dir=paths.get(
                            "composite_tmp"),
                    )
                    self._log_result("Playblast", results["mov"])
                self._advance_progress()
        finally:
            # Restore original camera name
            if renamed_cam and cmds.objExists(renamed_cam):
                cmds.rename(renamed_cam, original_cam_name)

        self._finish_export(results, paths, original_sel)

    def _export_face_track(self):
        """Export pipeline for Face Track tab."""
        errors, warnings = self._validate_face_track()
        if errors:
            for e in errors:
                self._log(e)
            cmds.confirmDialog(
                title="Export Errors",
                message="Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(errors)),
                button=["OK"],
            )
            return

        if warnings:
            result = cmds.confirmDialog(
                title="Warnings",
                message="Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(warnings)),
                button=["Continue", "Cancel"],
                defaultButton="Continue",
                cancelButton="Cancel",
                dismissString="Cancel",
            )
            if result == "Cancel":
                self._log("Export cancelled by user.")
                return

        original_sel = cmds.ls(selection=True)

        # Gather settings
        export_root = cmds.textFieldButtonGrp(
            self.export_root_field, query=True, text=True
        ).strip()
        camera = cmds.textFieldButtonGrp(
            self.ft_camera_field, query=True, text=True
        ).strip()
        static_geo = cmds.textFieldButtonGrp(
            self.ft_static_geo_field, query=True, text=True
        ).strip()
        face_meshes = []
        for entry in self.ft_face_mesh_entries:
            fm = cmds.textFieldButtonGrp(
                entry["field"], query=True, text=True
            ).strip()
            if fm:
                face_meshes.append(fm)
        do_ma = cmds.checkBox(self.ft_ma_checkbox, query=True, value=True)
        do_fbx = cmds.checkBox(self.ft_fbx_checkbox, query=True, value=True)
        do_mov = cmds.checkBox(self.ft_mov_checkbox, query=True, value=True)
        start_frame = cmds.intField(
            self.start_frame_field, query=True, value=True
        )
        end_frame = cmds.intField(
            self.end_frame_field, query=True, value=True
        )

        # Read version from UI field
        scene_short = cmds.file(
            query=True, sceneName=True, shortName=True
        )
        version_str = cmds.textFieldGrp(
            self.version_field, query=True, text=True).strip()
        if not version_str:
            version_str = "v01"
        scene_base = VersionParser.get_scene_base_name(scene_short)

        # Resolve versioned directories
        FolderManager.resolve_versioned_dir(
            export_root, scene_base, version_str
        )

        # Build paths and create directories (exclude PNG and MP4 temp
        # dirs — those are created on demand only when that format is selected)
        paths = FolderManager.build_export_paths(
            export_root, scene_base, version_str, tag="KTHead"
        )
        FolderManager.ensure_directories(
            {k: v for k, v in paths.items()
             if k not in ("png_dir", "png_file",
                          "mp4_tmp_dir", "mp4_tmp_file",
                          "composite_tmp", "composite_plate",
                          "composite_color", "composite_matte")})

        dir_path = os.path.dirname(paths.get("ma", paths.get("fbx", "")))
        self._log("Exporting to: {}".format(dir_path))

        exporter = Exporter(self._log)
        results = {}

        # Progress bar
        total_formats = sum([do_ma, do_fbx, do_mov])
        self._reset_progress(total_formats)

        # Rename camera to cam_main for all exports
        renamed_cam = None
        original_cam_name = camera
        baked_abc_cam = False
        try:
            if camera:
                if camera == "cam_main" and cmds.objExists(camera):
                    # Already named correctly — no rename needed
                    pass
                elif cmds.objExists(camera):
                    renamed_cam = cmds.rename(camera, "cam_main")
                    camera = renamed_cam
                elif cmds.objExists("cam_main"):
                    renamed_cam = "cam_main"
                    camera = "cam_main"
                else:
                    self._log(
                        "Camera not found. See Script Editor.")
                    camera = None

            # Detect Alembic-driven camera and bake before exports
            if camera and cmds.objExists(camera):
                cam_shapes = cmds.listRelatives(
                    camera, shapes=True, type="camera") or []
                abc_nodes = set()
                # Check transform TRS channels
                for attr in ("tx", "ty", "tz", "rx", "ry", "rz",
                             "sx", "sy", "sz"):
                    conns = cmds.listConnections(
                        "{}.{}".format(camera, attr),
                        source=True, destination=False) or []
                    for c in conns:
                        if cmds.nodeType(c) == "AlembicNode":
                            abc_nodes.add(c)
                # Check camera shape focalLength
                for shp in cam_shapes:
                    conns = cmds.listConnections(
                        "{}.focalLength".format(shp),
                        source=True, destination=False) or []
                    for c in conns:
                        if cmds.nodeType(c) == "AlembicNode":
                            abc_nodes.add(c)
                if abc_nodes:
                    self._log("Baking Alembic camera...")
                    cmds.undoInfo(openChunk=True)
                    baked_abc_cam = True
                    trs = ["tx", "ty", "tz", "rx", "ry", "rz",
                           "sx", "sy", "sz"]
                    # Unlock TRS channels
                    for a in trs:
                        try:
                            cmds.setAttr(
                                "{}.{}".format(camera, a),
                                lock=False, keyable=True,
                                channelBox=True)
                        except Exception:
                            pass
                    # Bake transform channels
                    cmds.bakeResults(
                        camera,
                        t=(int(start_frame), int(end_frame)),
                        at=trs,
                        simulation=True,
                        preserveOutsideKeys=True,
                        minimizeRotation=True,
                    )
                    # Bake focal length on camera shape
                    for shp in cam_shapes:
                        try:
                            cmds.setAttr(
                                "{}.focalLength".format(shp),
                                lock=False, keyable=True)
                        except Exception:
                            pass
                        cmds.bakeResults(
                            shp,
                            t=(int(start_frame), int(end_frame)),
                            at=["focalLength"],
                            simulation=True,
                            preserveOutsideKeys=True,
                        )
                    # Disconnect Alembic sources (keep baked animCurves)
                    all_plugs = ["{}.{}".format(camera, a)
                                 for a in trs]
                    for shp in cam_shapes:
                        all_plugs.append(
                            "{}.focalLength".format(shp))
                    for plug in all_plugs:
                        conns = cmds.listConnections(
                            plug, source=True, destination=False,
                            plugs=True,
                            skipConversionNodes=True) or []
                        for src_plug in conns:
                            src_node = src_plug.split(".")[0]
                            if cmds.nodeType(src_node).startswith(
                                    "animCurve"):
                                continue
                            try:
                                cmds.disconnectAttr(src_plug, plug)
                            except Exception:
                                pass
                    sys.stderr.write(
                        "[ExportGenie] Baked Alembic camera: {} "
                        "({} AlembicNode(s) disconnected).\n".format(
                            camera, len(abc_nodes)))

            if do_ma:
                # MA export: import references, convert Alembic
                # vertex animation to blendshapes, and strip
                # namespaces so the exported .ma is fully
                # self-contained (no external .ma/.mb/.abc
                # dependencies).  Restored via undo.
                static_geos = [static_geo] if static_geo else []
                cmds.undoInfo(openChunk=True)
                ma_prep = {"base_meshes": []}
                try:
                    # Import references
                    all_refs = cmds.ls(type="reference") or []
                    refs_imported = 0
                    for ref_node in all_refs:
                        if ref_node == "sharedReferenceNode":
                            continue
                        try:
                            cmds.file(
                                referenceNode=ref_node,
                                importReference=True)
                            refs_imported += 1
                        except Exception:
                            pass
                    if refs_imported:
                        self._log("Importing references...")

                    # Strip namespaces
                    all_ns = cmds.namespaceInfo(
                        listOnlyNamespaces=True, recurse=True
                    ) or []
                    skip_ns = {"UI", "shared"}
                    all_ns = [ns for ns in all_ns if ns not in skip_ns]
                    all_ns.sort(key=len, reverse=True)
                    for ns in all_ns:
                        try:
                            cmds.namespace(
                                removeNamespace=ns,
                                mergeNamespaceWithRoot=True)
                        except Exception:
                            pass

                    # Resolve names after namespace strip
                    def _resolve(name):
                        if not name:
                            return name
                        long_names = cmds.ls(name, long=True)
                        if long_names:
                            return long_names[0]
                        short = name.rsplit(":", 1)[-1]
                        long_names = cmds.ls(short, long=True)
                        if len(long_names) == 1:
                            return long_names[0]
                        return name

                    resolved_meshes = [_resolve(fm) for fm in face_meshes]
                    resolved_statics = [_resolve(sg) for sg in static_geos]
                    resolved_cam = _resolve(camera) if camera else camera

                    # Convert Alembic vertex animation to
                    # blendshapes so the .ma has no .abc dependency.
                    self._log("Preparing MA export...")
                    ma_prep = exporter.prepare_face_track_for_export(
                        resolved_meshes, start_frame, end_frame
                    )

                    # Export the converted meshes (blendshape bases
                    # replace the originals in the selection)
                    export_nodes = ma_prep.get(
                        "select_for_export", resolved_meshes)
                    results["ma"] = exporter.export_ma(
                        paths["ma"], resolved_cam,
                        export_nodes, [], resolved_statics,
                        start_frame=start_frame, end_frame=end_frame,
                    )
                except Exception as exc:
                    self._log(
                        "MA export failed. See Script Editor.")
                    sys.stderr.write(
                        "[ExportGenie] MA error: {}\n".format(exc))
                    results["ma"] = False
                finally:
                    cmds.undoInfo(closeChunk=True)
                    try:
                        cmds.undo()
                        self._log("Scene restored.")
                    except Exception:
                        self._log(
                            "Undo failed. See Script Editor.")
                    # Safety net: delete any surviving artifacts
                    for bm in ma_prep.get("base_meshes", []):
                        if cmds.objExists(bm):
                            try:
                                cmds.delete(bm)
                            except Exception:
                                pass
                self._log_result("MA", results["ma"])
                self._advance_progress()

            if do_fbx:
                self._log("Preparing FBX export...")
                cmds.undoInfo(openChunk=True)
                prep = {
                    "base_meshes": [],
                    "select_for_export": [],
                }
                try:
                    prep = exporter.prepare_face_track_for_export(
                        face_meshes, start_frame, end_frame
                    )

                    if not prep["select_for_export"]:
                        self._log("No geometry found to export.")
                        results["fbx"] = False
                    else:
                        self._log("FBX export...")
                        static_geos = [static_geo] if static_geo else []
                        results["fbx"] = exporter.export_fbx(
                            paths["fbx"], camera,
                            prep["select_for_export"], [],
                            static_geos, start_frame, end_frame,
                            export_input_connections=True,
                        )
                except Exception as exc:
                    self._log(
                        "FBX export failed. See Script Editor.")
                    results["fbx"] = False
                finally:
                    cmds.undoInfo(closeChunk=True)
                    try:
                        cmds.undo()
                        self._log("Scene restored.")
                    except Exception:
                        self._log(
                            "Undo failed. See Script Editor.")

                    # Safety net: delete any surviving artifacts
                    artifacts = [
                        a for a in prep.get("base_meshes", [])
                        if cmds.objExists(a)
                    ]
                    if artifacts:
                        for artifact in artifacts:
                            try:
                                cmds.delete(artifact)
                            except Exception:
                                pass

                self._log_result("FBX", results.get("fbx", False))
                self._advance_progress()

            if do_mov:
                fmt_choice = cmds.optionMenu(
                    self.ft_mov_format_menu, query=True, value=True)
                png_mode = "PNG" in fmt_choice
                mp4_mode = ".mp4" in fmt_choice
                if mp4_mode and not Exporter._find_ffmpeg():
                    self._log(
                        "Playblast skipped — ffmpeg not found.")
                    results["mov"] = False
                else:
                    if mp4_mode:
                        pb_path = paths["mp4_tmp_file"]
                        if not os.path.exists(paths["mp4_tmp_dir"]):
                            os.makedirs(paths["mp4_tmp_dir"])
                    elif png_mode:
                        pb_path = paths["png_file"]
                        if not os.path.exists(paths["png_dir"]):
                            os.makedirs(paths["png_dir"])
                    else:
                        pb_path = paths["mov"]
                    self._log("Preparing playblast...")
                    raw_pb = cmds.checkBox(
                        self.pb_raw_playblast_cb, query=True,
                        value=True)
                    custom_vt = cmds.checkBox(
                        self.pb_custom_vt_cb, query=True,
                        value=True)
                    chk_scale = cmds.intSliderGrp(
                        self.pb_checker_scale, query=True, value=True)
                    chk_color = tuple(cmds.colorSliderGrp(
                        self.pb_checker_color, query=True,
                        rgbValue=True))
                    chk_opacity = cmds.intSliderGrp(
                        self.pb_checker_opacity, query=True,
                        value=True)
                    aa16 = cmds.checkBox(
                        self.pb_aa16_cb, query=True, value=True)
                    far_clip = cmds.intSliderGrp(
                        self.pb_far_clip, query=True, value=True)
                    show_hud = cmds.checkBox(
                        self.pb_hud_overlay_cb, query=True,
                        value=True)
                    results["mov"] = exporter.export_playblast(
                        pb_path, camera, start_frame, end_frame,
                        matchmove_geo=face_meshes,
                        checker_scale=chk_scale,
                        checker_color=chk_color,
                        checker_opacity=chk_opacity,
                        raw_playblast=raw_pb,
                        render_raw_srgb=not custom_vt,
                        msaa_16=aa16,
                        far_clip=far_clip,
                        png_mode=png_mode,
                        mp4_mode=mp4_mode,
                        mp4_output=paths.get("mp4"),
                        show_hud=show_hud,
                        composite_plate_path=paths.get(
                            "composite_plate"),
                        composite_color_path=paths.get(
                            "composite_color"),
                        composite_matte_path=paths.get(
                            "composite_matte"),
                        composite_tmp_dir=paths.get(
                            "composite_tmp"),
                    )
                    self._log_result("Playblast", results["mov"])
                self._advance_progress()
        finally:
            # Undo Alembic camera bake (restores original connections)
            if baked_abc_cam:
                try:
                    cmds.undoInfo(closeChunk=True)
                    cmds.undo()
                except Exception:
                    self._log(
                        "Undo camera bake failed. See Script Editor.")
            # Restore original camera name
            if renamed_cam and cmds.objExists(renamed_cam):
                cmds.rename(renamed_cam, original_cam_name)

        self._finish_export(results, paths, original_sel)

    def _finish_export(self, results, paths, original_sel):
        """Restore selection and show completion dialog."""
        self._hide_progress()

        if original_sel:
            cmds.select(original_sel, replace=True)
        else:
            cmds.select(clear=True)

        failed = [k for k, v in results.items() if not v]
        if failed:
            self._log("Export finished with errors. See Script Editor.")
            cmds.confirmDialog(
                title="Export Complete (with errors)",
                message="Export Genie {}\n\nSome exports failed: {}\nSee Script Editor for details.".format(
                    TOOL_VERSION,
                    ", ".join(f.upper() for f in failed)
                ),
                button=["OK"],
            )
        else:
            self._log("Export complete.")
            cmds.confirmDialog(
                title="Export Complete",
                message="All exports completed successfully!",
                button=["OK"],
            )


# ---------------------------------------------------------------------------
# Entry Points
# ---------------------------------------------------------------------------
def launch():
    """Open the Export Genie UI. Called by the shelf button.

    Forces a module reload so dropping a new ExportGenie.py into the
    scripts folder and clicking the shelf button is enough to upgrade.
    """
    import importlib
    import ExportGenie as _self_mod
    importlib.reload(_self_mod)
    _self_mod._launch_inner()


def _launch_inner():
    """Internal launcher — called after the module has been reloaded."""
    global _ui_instance

    # Tear down existing workspace control if present
    if cmds.workspaceControl(WORKSPACE_CONTROL_NAME, exists=True):
        cmds.deleteUI(WORKSPACE_CONTROL_NAME)

    _ui_instance = MultiExportUI()

    cmds.workspaceControl(
        WORKSPACE_CONTROL_NAME,
        label="Export Genie  {}".format(TOOL_VERSION),
        floating=True,
        initialWidth=440,
        initialHeight=480,
        minimumWidth=380,
        retain=False,
        uiScript="import ExportGenie; ExportGenie._restore_ui()",
        closeCommand="import ExportGenie; ExportGenie._on_workspace_close()",
    )


def _restore_ui():
    """Called by workspaceControl uiScript to (re)build UI contents."""
    global _ui_instance
    # Force a module reload so the latest code is always used
    import importlib
    import ExportGenie as _self_mod
    importlib.reload(_self_mod)
    _self_mod._ui_instance = MultiExportUI()
    _ui_instance = _self_mod._ui_instance
    cmds.setParent(WORKSPACE_CONTROL_NAME)
    _ui_instance._build_ui_contents()


def _on_workspace_close():
    """Called by workspaceControl closeCommand."""
    global _ui_instance
    if _ui_instance is not None:
        _ui_instance._on_window_close()


# ---------------------------------------------------------------------------
# Installer
# ---------------------------------------------------------------------------
def _get_maya_app_dir():
    """Return the user's Maya application directory."""
    return cmds.internalVar(userAppDir=True)


def _get_scripts_dir():
    """Return the user's Maya scripts directory."""
    return os.path.join(_get_maya_app_dir(), "scripts")


def _get_icons_dir():
    """Return the user's Maya icons directory (create if needed)."""
    icons_dir = os.path.join(_get_maya_app_dir(), "prefs", "icons")
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    return icons_dir


def _install_icon():
    """Decode the embedded icon and write it to Maya's icons directory."""
    icon_path = os.path.join(_get_icons_dir(), ICON_FILENAME)
    icon_bytes = base64.b64decode(ICON_DATA)
    with open(icon_path, "wb") as f:
        f.write(icon_bytes)
    return icon_path


def _create_shelf_button():
    """Create the shelf button on the currently active shelf."""
    # Install the icon file
    _install_icon()

    # Get the active shelf
    top_shelf = mel.eval("$temp = $gShelfTopLevel")
    current_shelf = cmds.shelfTabLayout(
        top_shelf, query=True, selectTab=True
    )

    # Remove existing button to avoid duplicates (current + legacy names)
    _legacy_labels = {SHELF_BUTTON_LABEL, "Export_Genie"}
    existing = cmds.shelfLayout(
        current_shelf, query=True, childArray=True
    ) or []
    for btn in existing:
        try:
            if cmds.shelfButton(btn, query=True, exists=True):
                label = cmds.shelfButton(btn, query=True, label=True)
                if label in _legacy_labels:
                    cmds.deleteUI(btn)
        except Exception:
            pass

    # Create the button
    cmds.shelfButton(
        parent=current_shelf,
        label=SHELF_BUTTON_LABEL,
        annotation="Export Genie: Export to .ma, .fbx, .abc, .jsx",
        image1=ICON_FILENAME,
        command=(
            "import sys\n"
            "sys.modules.pop('ExportGenie', None)\n"
            "import ExportGenie\n"
            "ExportGenie.launch()\n"
        ),
        sourceType="python",
    )


def install():
    """Install the tool: copy to scripts dir and create shelf button."""
    source_file = os.path.abspath(__file__)
    scripts_dir = _get_scripts_dir()
    dest_file = os.path.join(scripts_dir, "ExportGenie.py")
    installed_items = []
    removed_items = []

    # --- Remove legacy versions (pre-rename) ---
    _legacy_scripts = ["maya_multi_export.py"]
    _legacy_icons = ["maya_multi_export.png"]
    _legacy_modules = ["maya_multi_export"]
    for old_script in _legacy_scripts:
        old_path = os.path.join(scripts_dir, old_script)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
                removed_items.append(("Removed old script", old_path))
            except OSError:
                pass
    icons_dir = _get_icons_dir()
    for old_icon in _legacy_icons:
        old_path = os.path.join(icons_dir, old_icon)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
                removed_items.append(("Removed old icon", old_path))
            except OSError:
                pass
    # Clear legacy .pyc caches
    pycache_dir = os.path.join(scripts_dir, "__pycache__")
    if os.path.isdir(pycache_dir):
        for old_mod in _legacy_modules:
            for f in os.listdir(pycache_dir):
                if f.startswith(old_mod) and f.endswith(".pyc"):
                    try:
                        os.remove(os.path.join(pycache_dir, f))
                    except OSError:
                        pass
    # Evict legacy modules from the interpreter
    for old_mod in _legacy_modules:
        sys.modules.pop(old_mod, None)

    # Copy self to Maya's scripts directory (if not already there)
    same_file = False
    try:
        same_file = os.path.samefile(source_file, dest_file)
    except (OSError, ValueError):
        same_file = (os.path.normpath(source_file)
                     == os.path.normpath(dest_file))
    if not same_file:
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
        shutil.copy2(source_file, dest_file)
    installed_items.append(("Script", dest_file))

    # Copy bundled bin/ directory (contains ffmpeg for Windows/macOS)
    source_dir = os.path.dirname(source_file)

    source_bin = os.path.join(source_dir, "bin")
    dest_bin = os.path.join(scripts_dir, "bin")
    if sys.platform == "win32":
        dest_ffmpeg = os.path.join(dest_bin, "win", "ffmpeg.exe")
    elif sys.platform == "darwin":
        dest_ffmpeg = os.path.join(dest_bin, "mac", "ffmpeg")
    else:
        dest_ffmpeg = None
    same_bin = False
    try:
        same_bin = (os.path.isdir(dest_bin)
                    and os.path.samefile(source_bin, dest_bin))
    except (OSError, ValueError):
        same_bin = (os.path.normpath(source_bin)
                    == os.path.normpath(dest_bin))
    if os.path.isdir(source_bin) and not same_bin:
        shutil.copytree(source_bin, dest_bin, dirs_exist_ok=True)
        for root, _dirs, files in os.walk(dest_bin):
            for fname in files:
                fpath = os.path.join(root, fname)
                installed_items.append(("Bundled", fpath))
    elif dest_ffmpeg and os.path.isfile(dest_ffmpeg):
        # No bin/ shipped with this drop, but a previous install
        # already placed ffmpeg — report it so the user knows.
        installed_items.append(("Already installed", dest_ffmpeg))
    elif dest_ffmpeg:
        # Neither source nor destination has ffmpeg — warn the user.
        installed_items.append((
            "NOT FOUND",
            "ffmpeg  (expected at {})".format(dest_ffmpeg)))

    # Ensure macOS ffmpeg binary is executable and
    # clear Gatekeeper quarantine attribute (runs on every install)
    if sys.platform == "darwin" and dest_ffmpeg and os.path.isfile(
            dest_ffmpeg):
        try:
            os.chmod(dest_ffmpeg, 0o755)
        except OSError:
            pass
        try:
            subprocess.run(
                ["xattr", "-d",
                 "com.apple.quarantine", dest_ffmpeg],
                check=False,
                capture_output=True)
        except Exception:
            pass

    # Clear compiled .pyc cache to ensure a fresh import
    pycache_dir = os.path.join(scripts_dir, "__pycache__")
    if os.path.isdir(pycache_dir):
        for f in os.listdir(pycache_dir):
            if f.startswith(TOOL_NAME) and f.endswith(".pyc"):
                try:
                    os.remove(os.path.join(pycache_dir, f))
                except OSError:
                    pass

    # Remove stale module and re-import fresh from scripts dir
    sys.modules.pop(TOOL_NAME, None)
    mod = __import__(TOOL_NAME)

    # Create shelf button and show dialog using the freshly loaded module
    mod._create_shelf_button()
    icon_path = os.path.join(_get_icons_dir(), ICON_FILENAME)
    if os.path.isfile(icon_path):
        installed_items.append(("Shelf icon", icon_path))

    # Build the installed-items summary
    summary_lines = []
    for label, path in installed_items:
        summary_lines.append("  {}:  {}".format(label, path))
    summary = "\n".join(summary_lines)

    # Build the removed-items summary (if any legacy files were cleaned up)
    removed_section = ""
    if removed_items:
        removed_lines = []
        for label, path in removed_items:
            removed_lines.append("  {}:  {}".format(label, path))
        removed_section = (
            "\nCleaned up old version:\n"
            "{}\n".format("\n".join(removed_lines)))

    cmds.confirmDialog(
        title="Install Complete",
        message=(
            "SUCCESS!\n\n"
            "Export Genie {} installed.\n\n"
            "Installed files:\n"
            "{}\n"
            "{}\n"
            "A shelf button has been added to your current shelf.\n"
            "Click it to open the export tool."
        ).format(mod.TOOL_VERSION, summary, removed_section),
        button=["OK"],
    )


def onMayaDroppedPythonFile(*args, **kwargs):
    """Maya drag-and-drop hook — called when this file is dropped into the viewport."""
    install()
