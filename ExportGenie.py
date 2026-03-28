"""
ExportGenie.py  v12
Export Genie — Export scenes to .ma, .fbx, .abc with auto versioning.

Drag and drop this file into Maya's viewport to install.
Compatible with Maya 2025+.
"""

import ctypes
import datetime
import math
import os
import re
import struct
import subprocess
import sys
import shutil
import base64
import traceback
from functools import partial

import maya.cmds as cmds
import maya.mel as mel

# PySide6 (Maya 2026+) with PySide2 fallback (Maya 2025 and earlier)
try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QScrollArea,
        QCheckBox, QPushButton, QLineEdit, QComboBox, QSpinBox, QSlider,
        QProgressBar, QTextEdit, QLabel, QMessageBox, QFileDialog,
        QColorDialog, QSizePolicy, QFrame, QApplication,
    )
    from PySide6.QtCore import Qt, Signal, QSize
    from PySide6.QtGui import QColor, QFont, QTextCursor
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QScrollArea,
        QCheckBox, QPushButton, QLineEdit, QComboBox, QSpinBox, QSlider,
        QProgressBar, QTextEdit, QLabel, QMessageBox, QFileDialog,
        QColorDialog, QSizePolicy, QFrame, QApplication,
    )
    from PySide2.QtCore import Qt, Signal, QSize
    from PySide2.QtGui import QColor, QFont, QTextCursor
    from shiboken2 import wrapInstance
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TOOL_NAME = "ExportGenie"
TOOL_VERSION = "v12.5"
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

    @staticmethod
    def parse_folder_name(folder_name):
        """Parse an export folder name into base and version.

        The folder name follows the pattern:
            {shot}_{plate}_{tag}_{version}
        e.g. "SHOT001_pl01_track_v03"
             -> base="SHOT001_pl01", version="v03"

        The base is everything before the tag, the version is the
        trailing _v## segment, and the tag (between base and version)
        is discarded — callers supply their own per-format tag.

        Returns:
            tuple: (base, version_str) e.g. ("SHOT001_pl01", "v03").
                   Falls back to (folder_name, "v01") if no version found.
        """
        matches = VersionParser.VERSION_PATTERN.findall(folder_name)
        if matches:
            ver_digits = matches[-1]
            version_str = "v{:02d}".format(int(ver_digits))
            last_ver = "_v" + ver_digits
            idx = folder_name.rfind(last_ver)
            before_ver = folder_name[:idx]
            # Drop the tag segment (last underscore-separated part
            # before the version)
            if "_" in before_ver:
                base = before_ver.rsplit("_", 1)[0]
            else:
                base = before_ver
            return (base, version_str)
        return (folder_name, "v01")


# ---------------------------------------------------------------------------
# FolderManager
# ---------------------------------------------------------------------------
class FolderManager(object):
    """Create and manage export folder structure."""

    @staticmethod
    def build_export_paths(export_root, scene_base_name, version_str,
                           tag="track", qc_tag="track",
                           folder_name=None):
        """Build the full set of export paths.

        Args:
            scene_base_name: Base name portion (e.g. "SHOT001_pl01").
            version_str: Version string e.g. "v01".
            tag: Naming tag for export files (ma, fbx, abc).
                 "cam" for Camera Track, "charMM" for Matchmove,
                 "KTHead" for Face Track.
            qc_tag: Naming tag for QC playblast files (mov, png, mp4).
                    Defaults to "track" for all tabs.
            folder_name: Full export folder name. When provided, used
                as the subdirectory under export_root instead of
                scene_base_name.

        Returns:
            dict: {"ma": path, "fbx": path, "abc": path, "mov": path, ...}
        """
        paths = {}
        dir_name = folder_name if folder_name else scene_base_name
        dir_path = os.path.join(export_root, dir_name)
        for fmt, ext in [("ma", ".ma"), ("fbx", ".fbx"), ("abc", ".abc"),
                         ("usd", ".usd")]:
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
        paths["composite_crown"] = os.path.join(
            composite_tmp, "crown", qc_base)
        return paths

    @staticmethod
    def ensure_directories(paths):
        """Create all necessary directories for the given paths."""
        for fmt, file_path in paths.items():
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    @staticmethod
    def build_ae_export_paths(export_root, scene_base_name, version_str,
                              geo_names, folder_name=None):
        """Build export paths for AE JSX + OBJ files.

        Args:
            export_root: Base export directory.
            scene_base_name: Base name portion (e.g. "SHOT001_pl01").
            version_str: Version string e.g. "v01".
            geo_names: List of geometry child names for OBJ files.
            folder_name: Full export folder name (used as parent dir).

        Returns:
            dict: {"jsx": full_path, "obj": {geo_name: full_path, ...}}
        """
        main_dir_name = folder_name if folder_name else scene_base_name
        ae_dir_name = "{base}_afterEffects_{ver}".format(
            base=scene_base_name, ver=version_str)
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
            obj_name = "{base}_{geo}_{ver}.obj".format(
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
        """Ensure the export directory exists.

        The folder name is the user-supplied export name (scene_base_name).

        Returns:
            str: Path to the export directory.
        """
        target_dir = os.path.join(export_root, scene_base_name)
        return target_dir

    @staticmethod
    def resolve_ae_dir(parent_dir, scene_base_name, version_str):
        """Ensure the AE export subdirectory exists.

        Returns:
            str: Path to the AE directory.
        """
        target_name = "{base}_afterEffects_{ver}".format(
            base=scene_base_name, ver=version_str)
        target_dir = os.path.join(parent_dir, target_name)

        return target_dir


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# QC Face Track Crown
# ---------------------------------------------------------------------------

def _qc_set_curve_display(crv, color_index=17, line_width=2.0,
                          template=False):
    """Apply display overrides to NURBS curve shapes."""
    shapes = cmds.listRelatives(crv, s=True, f=True) or []
    for s in shapes:
        if cmds.nodeType(s) != "nurbsCurve":
            continue
        try:
            cmds.setAttr("{}.overrideEnabled".format(s), 1)
            cmds.setAttr("{}.overrideColor".format(s),
                         int(color_index))
        except Exception:
            pass
        if cmds.attributeQuery("lineWidth", n=s, exists=True):
            try:
                cmds.setAttr("{}.lineWidth".format(s),
                             float(line_width))
            except Exception:
                pass
    if template:
        try:
            cmds.setAttr("{}.template".format(crv), 1)
        except Exception:
            pass


def _qc_make_closed_curve(points, name):
    """Create a closed degree-3 NURBS curve from *points*."""
    if points[0] != points[-1]:
        points = list(points) + [points[0]]
    crv = cmds.curve(d=3, p=points, name=name)
    closed = cmds.closeCurve(crv, ch=False, rpo=True, ps=True)
    if isinstance(closed, (list, tuple)) and closed:
        for item in reversed(closed):
            if (cmds.objExists(item)
                    and cmds.nodeType(item) == "transform"):
                crv = item
                break
    return crv


def _qc_bbox_radius_and_center(node, pad=1.25):
    """Return *(radius, centerXYZ, yMin, yMax)* from the world bbox."""
    bb = cmds.exactWorldBoundingBox(node)
    xmin, ymin, zmin, xmax, ymax, zmax = bb
    cx = (xmin + xmax) * 0.5
    cy = (ymin + ymax) * 0.5
    cz = (zmin + zmax) * 0.5
    dx = xmax - xmin
    dz = zmax - zmin
    radius = (max(dx, dz) * 0.5) * float(pad)
    return radius, (cx, cy, cz), ymin, ymax


def create_qc_crown(name="QC_head", radius=14.0, height=0.0,
                     ring_points=20, spike_len=4.0, spike_count=8,
                     add_crosshair=True, add_vertical_prongs=True,
                     prong_len=6.0, color_index=17, line_width=2.0,
                     template=False):
    """Build the QC crown curve group used for face track playblasts."""
    ring_points = max(8, int(ring_points))
    spike_count = max(4, int(spike_count))
    radius = float(radius)
    height = float(height)
    spike_len = float(spike_len)
    prong_len = float(prong_len)

    grp = cmds.group(em=True, name="{}_GRP".format(name))
    cmds.setAttr("{}.translateY".format(grp), height)

    # Base ring (XZ plane)
    ring_pts = []
    for i in range(ring_points):
        ang = 2.0 * math.pi * (i / float(ring_points))
        ring_pts.append(
            (math.cos(ang) * radius, 0.0,
             math.sin(ang) * radius))
    ring = _qc_make_closed_curve(ring_pts,
                                 "{}_ring_CRV".format(name))
    cmds.parent(ring, grp)

    # Spiky ring
    spike_indices = set(
        int(round((s / float(spike_count)) * ring_points))
        % ring_points for s in range(spike_count))
    spike_pts = []
    for i in range(ring_points):
        ang = 2.0 * math.pi * (i / float(ring_points))
        base = (math.cos(ang) * radius, 0.0,
                math.sin(ang) * radius)
        if i in spike_indices:
            spike = (math.cos(ang) * (radius + spike_len), 0.0,
                     math.sin(ang) * (radius + spike_len))
            spike_pts.append(base)
            spike_pts.append(spike)
        else:
            spike_pts.append(base)
    spiky = _qc_make_closed_curve(spike_pts,
                                  "{}_spiky_CRV".format(name))
    cmds.parent(spiky, grp)

    # Crosshair + center square
    if add_crosshair:
        cs = radius * 0.35
        xline = cmds.curve(
            d=1, p=[(-cs, 0, 0), (cs, 0, 0)],
            name="{}_X_CRV".format(name))
        zline = cmds.curve(
            d=1, p=[(0, 0, -cs), (0, 0, cs)],
            name="{}_Z_CRV".format(name))
        cmds.parent(xline, zline, grp)
        sq = radius * 0.12
        square = _qc_make_closed_curve(
            [(-sq, 0, -sq), (sq, 0, -sq),
             (sq, 0, sq), (-sq, 0, sq)],
            "{}_centerSquare_CRV".format(name))
        cmds.parent(square, grp)

    # Vertical prongs (Y-axis)
    if add_vertical_prongs:
        pr = radius * 0.75
        prongs = []
        for x, z, label in [(pr, 0, "E"), (-pr, 0, "W"),
                             (0, pr, "N"), (0, -pr, "S")]:
            p = cmds.curve(
                d=1,
                p=[(x, -prong_len * 0.5, z),
                   (x, prong_len * 0.5, z)],
                name="{}_prong{}_CRV".format(name, label))
            prongs.append(p)
        cmds.parent(prongs, grp)

    # Apply display overrides
    kids = cmds.listRelatives(
        grp, c=True, type="transform", f=True) or []
    for k in kids:
        shapes = cmds.listRelatives(k, s=True, f=True) or []
        if any(cmds.nodeType(s) == "nurbsCurve" for s in shapes):
            _qc_set_curve_display(
                k, color_index=color_index,
                line_width=line_width, template=template)

    cmds.select(grp)
    return grp


def create_qc_crown_from_mesh(name="QC_head", pad=1.25,
                               spike_len_ratio=0.25,
                               ring_points=24, spike_count=8,
                               color_index=17, line_width=2.0,
                               template=False, add_crosshair=True,
                               add_vertical_prongs=True,
                               y_fraction=2.5 / 3.0):
    """Create a QC crown sized and constrained to the selected mesh.

    Select the KeenTools-tracked head mesh TRANSFORM (the animated
    mesh) first, then call this.  The crown is positioned at the
    upper portion of the bounding box, then point + orient
    constrained to the mesh with maintainOffset.

    Returns:
        tuple: (group, pointConstraint, orientConstraint)
    """
    sel = cmds.ls(sl=True, long=True) or []
    if not sel:
        raise RuntimeError(
            "Select the tracked head mesh transform, then run again.")
    if len(sel) != 1:
        raise RuntimeError(
            "Select only ONE node: the tracked head mesh transform.")

    head = sel[0]
    radius, center, ymin, ymax = _qc_bbox_radius_and_center(
        head, pad=pad)
    head_h = max(1e-6, ymax - ymin)
    spike_len = max(0.05, radius * float(spike_len_ratio))
    y_fraction = max(0.0, min(1.0, float(y_fraction)))
    crown_pos = [center[0], ymin + head_h * y_fraction, center[2]]

    grp = create_qc_crown(
        name=name, radius=radius, height=0.0,
        ring_points=ring_points, spike_len=spike_len,
        spike_count=spike_count, add_crosshair=add_crosshair,
        add_vertical_prongs=add_vertical_prongs,
        prong_len=max(0.05, radius * 0.45),
        color_index=color_index, line_width=line_width,
        template=template)

    # Position then constrain to the mesh transform.
    # The mesh transform has animCurves on TRS from the face
    # tracking solve — the constraints follow this animation.
    cmds.xform(grp, ws=True, t=crown_pos)
    pc = cmds.pointConstraint(head, grp, mo=True)[0]
    oc = cmds.orientConstraint(head, grp, mo=True)[0]

    cmds.select(grp)
    return grp, pc, oc


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

    @staticmethod
    def _has_drawtext():
        """Return True if the bundled ffmpeg supports the drawtext filter."""
        ffmpeg_path = Exporter._find_ffmpeg()
        if not ffmpeg_path:
            return False
        try:
            result = subprocess.run(
                [ffmpeg_path, "-hide_banner", "-filters"],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=getattr(
                    subprocess, "CREATE_NO_WINDOW", 0),
            )
            return "drawtext" in result.stdout
        except Exception:
            return False

    @staticmethod
    def _run_ffmpeg(cmd, filter_complex=None, log_prefix="ffmpeg"):
        """Run an ffmpeg command with a filter_complex graph.

        On Windows, writes the filter to a temp script file and
        uses ``-filter_complex_script`` to avoid colon-escaping
        issues with font paths.  On macOS/Linux, passes the filter
        inline via ``-filter_complex`` (no escaping issues).

        The filter args are inserted just before ``-map`` so ffmpeg
        sees them before output options.

        Returns:
            subprocess.CompletedProcess
        """
        import tempfile as _tf

        script_path = None
        try:
            if filter_complex:
                if sys.platform == "win32":
                    # Windows: write to temp file to avoid colon
                    # escaping issues with fontfile paths.
                    fd, script_path = _tf.mkstemp(
                        suffix=".txt", prefix="ffmpeg_filter_")
                    with os.fdopen(fd, "w") as fh:
                        fh.write(filter_complex)
                    fc_args = ["-filter_complex_script",
                               script_path]
                else:
                    # macOS / Linux: pass inline.
                    fc_args = ["-filter_complex", filter_complex]

                if "-map" in cmd:
                    idx = cmd.index("-map")
                    cmd[idx:idx] = fc_args
                else:
                    cmd.extend(fc_args)

            sys.stderr.write("{} cmd: {}\n".format(
                log_prefix, " ".join(cmd)))

            result = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=600,
                creationflags=getattr(
                    subprocess, "CREATE_NO_WINDOW", 0),
            )
            return result
        finally:
            if script_path:
                try:
                    os.remove(script_path)
                except Exception:
                    pass

    @staticmethod
    def _get_image_plane_resolution(camera):
        """Return (width, height) from the first image plane on *camera*.

        Reads the ``coverageX`` / ``coverageY`` attributes from the
        imagePlane shape node, which reflect the source image
        dimensions.  Falls back to (1920, 1080) if no image plane
        is found or the attributes cannot be read.
        """
        default = (1920, 1080)
        if not camera or not cmds.objExists(camera):
            return default
        cam_shapes = cmds.listRelatives(
            camera, shapes=True, type="camera") or []
        for shp in cam_shapes:
            img_planes = cmds.listConnections(
                "{}.imagePlane".format(shp),
                type="imagePlane") or []
            for ip in img_planes:
                # Get the imagePlane shape node
                ip_shapes = cmds.listRelatives(
                    ip, shapes=True, type="imagePlane") or []
                ip_shape = ip_shapes[0] if ip_shapes else ip
                try:
                    w = cmds.getAttr(
                        "{}.coverageX".format(ip_shape))
                    h = cmds.getAttr(
                        "{}.coverageY".format(ip_shape))
                    if w and h and w > 0 and h > 0:
                        return (int(w), int(h))
                except Exception:
                    pass
        return default

    @staticmethod
    def _find_hud_font():
        """Locate a monospace font for ffmpeg drawtext overlay.

        Returns:
            str or None: Absolute path to a .ttf/.ttc font file.
        """
        if sys.platform == "win32":
            candidates = [
                os.path.join(os.environ.get("WINDIR", r"C:\Windows"),
                             "Fonts", "consola.ttf"),
                os.path.join(os.environ.get("WINDIR", r"C:\Windows"),
                             "Fonts", "arial.ttf"),
            ]
        elif sys.platform == "darwin":
            candidates = [
                "/System/Library/Fonts/Menlo.ttc",
                "/System/Library/Fonts/SFNSMono.ttf",
                "/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]
        else:
            candidates = []
        for f in candidates:
            if os.path.isfile(f):
                return f
        return None

    def _build_hud_drawtext(self, start_frame, focal_length=None,
                            resolution=None):
        """Build ffmpeg drawtext filter chain for metadata overlay.

        Returns a filter fragment (no leading/trailing semicolons)
        that reads from ``[pre_hud]`` and writes to ``[out]``.

        Args:
            start_frame: First frame number (int).
            focal_length: Camera focal length in mm, or None.

        Returns:
            str: drawtext filter chain string.
        """
        font_path = self._find_hud_font()
        # Common options: white text, drop shadow, large font
        font_opts = (
            "fontsize=32"
            ":fontcolor=white"
            ":shadowcolor=black@0.6"
            ":shadowx=2:shadowy=2"
        )
        if font_path:
            # Double-escape the colon for ffmpeg's two-level parsing:
            # Level 2 (filtergraph): \\: → \:
            # Level 1 (filter option): \: → :
            escaped = font_path.replace("\\", "/").replace(
                ":", "\\\\:")
            font_opts = "fontfile={}:{}".format(escaped, font_opts)

        start = int(start_frame)

        # Bottom-left: frame number (4-digit padded)
        frame_dt = (
            "drawtext={opts}"
            ":text='%{{eif\\:n+{start}\\:d\\:4}}'"
            ":x=30:y=h-th-30"
        ).format(opts=font_opts, start=start)

        # Bottom-right: FL | resolution | version | datetime
        now_str = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M")
        parts = []
        if focal_length is not None:
            parts.append("FL {:.1f}mm".format(focal_length))
        res = resolution or (1920, 1080)
        parts.append("{}x{}".format(res[0], res[1]))
        parts.append("{} {}".format(TOOL_NAME, TOOL_VERSION))
        parts.append(now_str)
        # Escape colons for ffmpeg drawtext syntax
        right_text = "   ".join(parts).replace(":", "\\:")

        meta_dt = (
            "drawtext={opts}:text='{text}'"
            ":x=w-tw-30:y=h-th-30"
        ).format(opts=font_opts, text=right_text)

        return "[pre_hud]{frame},{meta}[out]".format(
            frame=frame_dt, meta=meta_dt)

    def _encode_mp4(self, png_dir, png_base, start_frame, output_mp4,
                    show_hud=False, focal_length=None,
                    resolution=None):
        """Encode a PNG image sequence to H.264 .mp4 via bundled ffmpeg.

        Args:
            png_dir: Directory containing the PNG sequence.
            png_base: Base filename without frame number or extension.
            start_frame: First frame number in the sequence.
            output_mp4: Full path to the output .mp4 file.
            show_hud: If True, burn metadata text overlay via drawtext.
            focal_length: Camera focal length in mm (for HUD).

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
        ]
        vf_script = None
        if show_hud and self._has_drawtext():
            hud_filters = self._build_hud_drawtext(
                start_frame, focal_length, resolution=resolution)
            # Strip stream labels — single-input uses plain vf
            vf_script = hud_filters.replace(
                "[pre_hud]", "").replace("[out]", "")
        cmd.extend([
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-profile:v", "high",
            "-level", "4.2",
            "-preset", "ultrafast",
            "-crf", "18",
            "-movflags", "+faststart",
            output_mp4,
        ])

        self.log("Encoding MP4...")
        try:
            if vf_script is not None:
                if sys.platform == "win32":
                    # Windows: write to temp file to avoid colon
                    # escaping issues with fontfile paths.
                    import tempfile as _tf
                    fd, script_path = _tf.mkstemp(
                        suffix=".txt", prefix="ffmpeg_vf_")
                    try:
                        with os.fdopen(fd, "w") as fh:
                            fh.write(vf_script)
                        cmd.extend([
                            "-filter_script:v", script_path])
                        sys.stderr.write(
                            "ffmpeg cmd: {}\n".format(
                                " ".join(cmd)))
                        result = subprocess.run(
                            cmd,
                            stdin=subprocess.DEVNULL,
                            capture_output=True,
                            text=True,
                            timeout=600,
                            creationflags=getattr(
                                subprocess,
                                "CREATE_NO_WINDOW", 0),
                        )
                    finally:
                        try:
                            os.remove(script_path)
                        except Exception:
                            pass
                else:
                    # macOS / Linux: pass inline.
                    cmd.extend(["-vf", vf_script])
                    sys.stderr.write(
                        "ffmpeg cmd: {}\n".format(
                            " ".join(cmd)))
                    result = subprocess.run(
                        cmd,
                        stdin=subprocess.DEVNULL,
                        capture_output=True,
                        text=True,
                        timeout=600,
                        creationflags=getattr(
                            subprocess,
                            "CREATE_NO_WINDOW", 0),
                    )
            else:
                sys.stderr.write(
                    "ffmpeg cmd: {}\n".format(" ".join(cmd)))
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
                          opacity=1.0, png_output=False,
                          show_hud=False, focal_length=None,
                          resolution=None,
                          crown_dir=None, crown_base=None):
        """Composite passes (plate, color, matte, optional crown) via ffmpeg.

        Uses the matte as an alpha channel on the solid-color pass,
        then overlays it on the plate.  When crown_dir/crown_base are
        provided, a 4th input (QC spline crown on black) is
        screen-blended on top of the composite.

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
        ]

        if crown_dir and crown_base:
            crown_pattern = os.path.join(
                crown_dir, "{}.%04d.png".format(crown_base))
            cmd.extend([
                "-framerate", str(fps),
                "-start_number", start_num,
                "-i", crown_pattern,
            ])
            # 4-input: plate + color/matte overlay + crown screen blend
            filter_complex = (
                "[2:v]format=gray[matte];"
                "[1:v][matte]alphamerge,format=rgba,"
                "colorchannelmixer=aa={opacity:.4f}[fg];"
                "[0:v][fg]overlay=format=auto[base];"
                "[3:v]split[crown_color][crown_luma];"
                "[crown_luma]format=gray[crown_alpha];"
                "[crown_color][crown_alpha]alphamerge,"
                "format=rgba[crown_rgba];"
                "[base][crown_rgba]overlay=format=auto[out]"
            ).format(opacity=opacity_val)
        else:
            filter_complex = (
                "[2:v]format=gray[matte];"
                "[1:v][matte]alphamerge,format=rgba,"
                "colorchannelmixer=aa={opacity:.4f}[fg];"
                "[0:v][fg]overlay=format=auto[out]"
            ).format(opacity=opacity_val)

        if show_hud and self._has_drawtext():
            hud_chain = self._build_hud_drawtext(
                start_frame, focal_length, resolution=resolution)
            filter_complex = filter_complex.replace(
                "[out]", "[pre_hud]")
            filter_complex += ";" + hud_chain

        # Write filter_complex to a temp script file to avoid
        # Windows colon-escaping issues with fontfile paths.
        cmd.extend(["-map", "[out]"])

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
        try:
            result = self._run_ffmpeg(
                cmd, filter_complex=filter_complex,
                log_prefix="ffmpeg composite")
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

        UE5-conforming settings: Resample All ON, Tangents ON, Up Axis Z.

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
                mel_path = file_path.replace("\\", "/").replace('"', '\\"')
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
                   start_frame, end_frame, rig_roots=None):
        """Export camera + geo roots + rig roots + proxy geo as Alembic cache.

        Args:
            geo_roots: list of geo root transforms (or empty list).
            proxy_geos: list of static/proxy geo transforms (or empty list).
            rig_roots: list of rig root transforms (or empty list).
        """
        try:
            geo_roots = geo_roots or []
            proxy_geos = proxy_geos or []
            rig_roots = rig_roots or []
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

            if not camera and not geo_roots and not proxy_geos and not rig_roots:
                self.log("ABC skipped — nothing to export.")
                return False

            # Build root flags — camera, geo, static/proxy geo only.
            # Rig roots are excluded — ABC needs just the mesh,
            # camera, and any static geo.
            all_roots = geo_roots + proxy_geos
            if rig_roots:
                all_roots = all_roots + rig_roots
            cam_under_root = any(
                self._is_descendant_of(camera, gr)
                for gr in all_roots if gr
            )
            # Create metadata group and include as a root
            info_grp = self._create_metadata_grp()

            # Collect and resolve all root nodes to long paths
            root_candidates = ([camera] + geo_roots
                               + proxy_geos + [info_grp])
            resolved_roots = []
            for node in root_candidates:
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
                resolved_roots.append(long_names[0])

            # Remove any root that is a descendant of another root
            # — AbcExport errors on ancestor/descendant pairs.
            filtered_roots = []
            for root in resolved_roots:
                is_child = False
                for other in resolved_roots:
                    if other == root:
                        continue
                    if root.startswith(other + "|"):
                        is_child = True
                        break
                if not is_child:
                    filtered_roots.append(root)

            root_flags = ""
            for root in filtered_roots:
                root_flags += "-root '{}' ".format(
                    root.replace("'", "\\'"))

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
                file=abc_path.replace("'", "\\'"),
            )

            sys.stderr.write(
                "[ExportGenie] AbcExport job: {}\n".format(
                    job_string))

            try:
                cmds.AbcExport(j=job_string)
            finally:
                if cmds.objExists(info_grp):
                    try:
                        cmds.delete(info_grp)
                    except Exception:
                        pass
            if not os.path.isfile(file_path):
                self.log(
                    "ABC export completed but file not found.")
                sys.stderr.write(
                    "[ExportGenie] ABC file missing: "
                    "{}\n".format(file_path))
                return False
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                self.log(
                    "ABC export produced empty file.")
                sys.stderr.write(
                    "[ExportGenie] ABC file is 0 bytes: "
                    "{}\n".format(file_path))
                return False
            return True
        except Exception as e:
            self._log_error("ABC", e)
            sys.stderr.write(
                "[ExportGenie] ABC exception: {}\n".format(e))
            import traceback
            traceback.print_exc()
            return False

    # --- USD Export ---

    def export_usd(self, file_path, camera, geo_roots, proxy_geos,
                   start_frame, end_frame, rig_roots=None):
        """Export camera + geo roots + rig roots + proxy geo as USD.

        Args:
            geo_roots: list of geo root transforms (or empty list).
            proxy_geos: list of static/proxy geo transforms (or empty list).
            rig_roots: list of rig root transforms (or empty list).
        """
        try:
            geo_roots = geo_roots or []
            proxy_geos = proxy_geos or []
            rig_roots = rig_roots or []
            # Ensure mayaUsdPlugin is loaded
            try:
                is_loaded = cmds.pluginInfo(
                    "mayaUsdPlugin", query=True, loaded=True)
            except Exception:
                is_loaded = False
            if not is_loaded:
                try:
                    cmds.loadPlugin("mayaUsdPlugin")
                except Exception:
                    self.log("USD plugin not available. See Script Editor.")
                    cmds.confirmDialog(
                        title="USD Plugin Not Found",
                        message=(
                            "Export Genie {}\n\n"
                            "The USD plugin (mayaUsdPlugin) could not be "
                            "loaded.\n\n"
                            "To enable it, go to:\n"
                            "Windows > Settings/Preferences > Plug-in "
                            "Manager\n\n"
                            "Find 'mayaUsdPlugin' in the list and check "
                            "'Loaded'."
                        ).format(TOOL_VERSION),
                        button=["OK"],
                    )
                    return False

            if not camera and not geo_roots and not proxy_geos \
                    and not rig_roots:
                self.log("USD skipped — nothing to export.")
                return False

            # Build selection list — camera, geo, rig, proxy
            all_roots = geo_roots + proxy_geos
            if rig_roots:
                all_roots = all_roots + rig_roots
            cam_under_root = any(
                self._is_descendant_of(camera, gr)
                for gr in all_roots if gr
            )

            info_grp = self._create_metadata_grp()

            select_nodes = []
            if camera and not cam_under_root:
                select_nodes.append(camera)
            select_nodes.extend(geo_roots)
            select_nodes.extend(rig_roots)
            select_nodes.extend(proxy_geos)
            select_nodes.append(info_grp)

            # Filter out empty / missing nodes
            select_nodes = [
                n for n in select_nodes
                if n and cmds.objExists(n)]

            cmds.select(select_nodes, replace=True)

            usd_path = file_path.replace("\\", "/")

            sys.stderr.write(
                "[ExportGenie] USD export: {}\n".format(usd_path))

            try:
                cmds.mayaUSDExport(
                    file=usd_path,
                    selection=True,
                    frameRange=(int(start_frame), int(end_frame)),
                    frameStride=1.0,
                    exportSkels="auto",
                    exportSkin="auto",
                    exportBlendShapes=True,
                    exportVisibility=True,
                    eulerFilter=True,
                )
            finally:
                if cmds.objExists(info_grp):
                    try:
                        cmds.delete(info_grp)
                    except Exception:
                        pass
            if not os.path.isfile(file_path):
                self.log(
                    "USD export completed but file not found.")
                sys.stderr.write(
                    "[ExportGenie] USD file missing: "
                    "{}\n".format(file_path))
                return False
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                self.log(
                    "USD export produced empty file.")
                sys.stderr.write(
                    "[ExportGenie] USD file is 0 bytes: "
                    "{}\n".format(file_path))
                return False
            return True
        except Exception as e:
            self._log_error("USD", e)
            sys.stderr.write(
                "[ExportGenie] USD exception: {}\n".format(e))
            import traceback
            traceback.print_exc()
            return False

    # --- OBJ Export ---

    def export_obj(self, file_path, geo_node):
        """Export a single Maya object as OBJ in local space.

        Maya's OBJ exporter writes vertices in world space.  To avoid a
        double-offset in After Effects (where the JSX also sets position/
        rotation/scale), we duplicate the node, zero its transforms, and
        export the duplicate so vertices are written in local space.
        This handles locked, constrained, or Alembic-driven channels
        that would cause a direct xform set to silently fail.

        Args:
            file_path: Output .obj path.
            geo_node: Maya transform node to export.

        Returns:
            bool: True on success.
        """
        try:
            if not cmds.pluginInfo("objExport", query=True, loaded=True):
                cmds.loadPlugin("objExport")

            # Duplicate the geo and zero its transforms so the OBJ
            # exporter writes vertices in local space.  This avoids
            # issues with locked/constrained/Alembic-driven channels
            # where cmds.xform would silently fail.
            dup = cmds.duplicate(geo_node, rr=True, name="_obj_tmp_")[0]
            cmds.delete(dup, ch=True)
            try:
                cmds.parent(dup, world=True)
            except Exception:
                pass
            identity = [1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1]
            cmds.xform(dup, worldSpace=True, matrix=identity)

            try:
                cmds.select(dup, replace=True)
                cmds.file(
                    file_path,
                    exportSelected=True,
                    type="OBJexport",
                    force=True,
                    options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1",
                )
            finally:
                if cmds.objExists(dup):
                    cmds.delete(dup)

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

            # Step tangent on the peak key
            try:
                cmds.keyTangent(
                    w, time=(f, f), itt="stepnext", ott="step")
            except Exception:
                pass

            # Decay key at f+1 only if within the export range
            if f < end:
                cmds.setKeyframe(w, t=f + 1, v=0.0)
                try:
                    cmds.keyTangent(
                        w, time=(f + 1, f + 1),
                        itt="stepnext", ott="step")
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

        # --- Step 1a: Find constraint-driven non-joint transforms ---
        # IK control transforms, locators, and other non-joint nodes
        # under rig_roots may be driven by constraints (e.g. locator
        # → pointConstraint → IK control).  These must be baked
        # alongside joints so their animation survives constraint
        # deletion in Step 2.  Without this, IK controls snap to
        # rest pose and any still-active IK solvers produce wrong
        # results during the FBX plugin's internal re-bake.
        constraint_types = [
            "parentConstraint", "pointConstraint", "orientConstraint",
            "aimConstraint", "scaleConstraint", "poleVectorConstraint",
        ]
        constrained_xforms = []
        constrained_set = set()
        for root in (rig_roots or []):
            if not cmds.objExists(root):
                continue
            for ctype in constraint_types:
                constraints = cmds.listRelatives(
                    root, allDescendents=True, type=ctype,
                    fullPath=True
                ) or []
                for c in constraints:
                    # The constrained node is the constraint's parent
                    parent = cmds.listRelatives(
                        c, parent=True, fullPath=True)
                    if not parent:
                        continue
                    xform = parent[0]
                    if xform in constrained_set:
                        continue
                    # Skip joints — they're already in all_joints
                    if cmds.objectType(xform) == "joint":
                        continue
                    constrained_set.add(xform)
                    constrained_xforms.append(xform)
        if constrained_xforms:
            sys.stderr.write(
                "[ExportGenie]   Found {} constraint-driven "
                "transform(s) to bake\n".format(
                    len(constrained_xforms)))
            for cx in constrained_xforms[:10]:
                sys.stderr.write(
                    "[ExportGenie]     {}\n".format(cx))
            if len(constrained_xforms) > 10:
                sys.stderr.write(
                    "[ExportGenie]     ... and {} more\n".format(
                        len(constrained_xforms) - 10))

        sys.stderr.write(
            "[ExportGenie] Step 1: Bake animation\n")

        # Combine joints and constrained transforms into one bake
        # pass.  simulation=True evaluates the full DG at each frame,
        # capturing the correct result regardless of evaluation order.
        all_bake_nodes = list(all_joints) + constrained_xforms
        if all_bake_nodes:
            sys.stderr.write(
                "[ExportGenie]   Baking {} joint(s) + {} "
                "constrained transform(s)\n".format(
                    len(all_joints), len(constrained_xforms)))
            self.log("Baking animation...")
            # Unlock TRS channels before baking
            for node in all_bake_nodes:
                for a in trs:
                    try:
                        cmds.setAttr(
                            "{}.{}".format(node, a),
                            lock=False, keyable=True, channelBox=True)
                    except Exception:
                        pass
            cmds.bakeResults(
                all_bake_nodes,
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

        # Disconnect non-animCurve sources on all baked nodes
        for node in all_bake_nodes:
            for a in trs:
                plug = "{}.{}".format(node, a)
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

        Samples 3 vertex positions across 4 frames (start, 1/3, 2/3,
        end) to find meshes with real vertex deformation (vs.
        AlembicNode only driving TRS).  Multiple sample frames avoid
        false negatives when a mesh returns to rest pose at the
        endpoints.  Read-only — does not modify the scene.

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
        sf = int(start_frame)
        ef = int(end_frame)

        # Sample at start, 1/3, 2/3, and end for robust detection
        # (avoids missing meshes that return to rest pose at endpoints)
        sample_frames = sorted(set([
            sf,
            sf + max(1, (ef - sf) // 3),
            sf + max(1, (ef - sf) * 2 // 3),
            ef,
        ]))

        # Collect reference positions at first sample frame
        cmds.currentTime(sample_frames[0], edit=True)
        positions_ref = {}  # {long_name: (shape, indices, [pos, ...])}
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
                positions_ref[xform] = (shp, indices, pts)
                break  # one non-intermediate shape is enough

        # Compare against remaining sample frames
        for sample_frame in sample_frames[1:]:
            if not positions_ref:
                break
            cmds.currentTime(sample_frame, edit=True)
            still_checking = {}
            for long_name, (shp, indices, pts_a) in positions_ref.items():
                if long_name in vertex_anim_set:
                    continue
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
                if not found:
                    still_checking[long_name] = (shp, indices, pts_a)
            positions_ref = still_checking

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
                    # Non-mesh leaf (locator, null, etc.) — only
                    # include if it has driven transforms
                    if self._has_driven_transforms(node):
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
                         camera_track_mode=False, face_track_mode=False,
                         matchmove_geo=None,
                         checker_scale=8, checker_color=None,
                         checker_opacity=70, raw_playblast=False,
                         render_raw_srgb=True,
                         wireframe_shader=False,
                         wireframe_shader_geo=None,
                         msaa_16=False,
                         motion_blur=True,
                         far_clip=800000,
                         png_mode=False,
                         mp4_mode=False,
                         mp4_output=None,
                         show_hud=False,
                         composite_plate_path=None,
                         composite_color_path=None,
                         composite_matte_path=None,
                         composite_tmp_dir=None,
                         resolution=None):
        """Export a QC playblast.

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
        pb_width, pb_height = resolution or (1920, 1080)
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

            # Resolve focal length for metadata overlay
            hud_focal_length = None
            if camera:
                cam_shapes = cmds.listRelatives(
                    camera, shapes=True, type="camera") or []
                if cam_shapes:
                    try:
                        hud_focal_length = cmds.getAttr(
                            cam_shapes[0] + ".focalLength")
                    except Exception:
                        pass

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
                    label="",
                    labelFontSize="large",
                    dataFontSize="large",
                    blockSize="large",
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
                        hud_fl, section=8,
                        block=cmds.headsUpDisplay(nextFreeBlock=8),
                        label="",
                        labelFontSize="large",
                        blockSize="large",
                        command=lambda: "FL {:.1f}".format(
                            cmds.getAttr(
                                fl_shape + ".focalLength")),
                        attachToRefresh=True,
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
            original_shadows = None
            mm_meshes = []
            composite_rendered = False
            auto_qc_crown = None
            has_crown_pass = False

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

                # 3b. QC spline crown (Face Track only)
                original_nurbs_curves = cmds.modelEditor(
                    model_panel, query=True, nurbsCurves=True)
                if face_track_mode and cmds.objExists("QC_head_GRP"):
                    try:
                        cmds.delete("QC_head_GRP")
                    except Exception:
                        pass
                if face_track_mode:
                    # Create crown from the first face mesh.
                    # The picker may hold a group — find the
                    # actual animated mesh transform inside it.
                    crown_target = None
                    first_mesh = (matchmove_geo[0]
                                  if matchmove_geo else None)
                    if first_mesh and cmds.objExists(first_mesh):
                        # Check if the node itself has mesh shapes
                        shapes = cmds.listRelatives(
                            first_mesh, shapes=True,
                            type="mesh") or []
                        if shapes:
                            crown_target = first_mesh
                        else:
                            # Search all descendants for the first
                            # transform with mesh shapes (may be
                            # nested several levels deep).
                            descendants = cmds.listRelatives(
                                first_mesh,
                                allDescendents=True,
                                type="transform",
                                fullPath=True) or []
                            for desc in descendants:
                                desc_shapes = cmds.listRelatives(
                                    desc, shapes=True,
                                    type="mesh") or []
                                if desc_shapes:
                                    crown_target = desc
                                    break
                    if crown_target:
                        try:
                            cmds.select(crown_target, replace=True)
                            grp, _, _ = create_qc_crown_from_mesh(
                                name="QC_head")
                            auto_qc_crown = grp
                            cmds.select(clear=True)
                            sys.stderr.write(
                                "[ExportGenie] Auto-created "
                                "QC_head_GRP constrained to "
                                "{}\n".format(crown_target))
                        except Exception as e:
                            sys.stderr.write(
                                "[ExportGenie] QC crown "
                                "creation failed: {}\n".format(e))
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
                        "hardwareRenderingGlobals.motionBlurEnable",
                        motion_blur)
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
                        # HUD is rendered on the plate pass (bottom
                        # layer) so frame/FL text is visible in the
                        # final composite.  Color and matte passes
                        # use showOrnaments=False for clean keying.
                        self.log("Rendering plate pass...")
                        cmds.modelEditor(
                            model_panel, edit=True,
                            imagePlane=True, polymeshes=False,
                            nurbsSurfaces=False,
                            subdivSurfaces=False,
                            nurbsCurves=False)
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
                            showOrnaments=False,
                            framePadding=4,
                            percent=100,
                            quality=100,
                            widthHeight=[pb_width, pb_height],
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
                        original_shadows = cmds.modelEditor(
                            model_panel, query=True, shadows=True)
                        cmds.modelEditor(
                            model_panel, edit=True,
                            displayLights="flat",
                            shadows=False)

                        cmds.modelEditor(
                            model_panel, edit=True,
                            imagePlane=False, polymeshes=True,
                            nurbsSurfaces=True,
                            subdivSurfaces=True,
                            nurbsCurves=False)

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
                            widthHeight=[pb_width, pb_height],
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

                        cmds.modelEditor(
                            model_panel, edit=True,
                            nurbsCurves=False)
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
                            widthHeight=[pb_width, pb_height],
                        )

                        # --- Pass 4: Crown curves (Face Track only) ---
                        has_crown_pass = False
                        if (face_track_mode
                                and cmds.objExists("QC_head_GRP")
                                and cmds.listRelatives(
                                    "QC_head_GRP",
                                    allDescendents=True,
                                    type="nurbsCurve")
                                and composite_tmp_dir):
                            crown_path = os.path.join(
                                composite_tmp_dir, "crown",
                                os.path.basename(
                                    composite_matte_path))
                            crown_dir = os.path.dirname(crown_path)
                            if not os.path.exists(crown_dir):
                                os.makedirs(crown_dir)
                            self.log("Rendering crown pass...")
                            # Ensure black background for crown pass
                            cmds.displayRGBColor(
                                "background", 0, 0, 0)
                            cmds.displayRGBColor(
                                "backgroundTop", 0, 0, 0)
                            cmds.displayRGBColor(
                                "backgroundBottom", 0, 0, 0)
                            cmds.displayPref(displayGradient=False)
                            # Re-apply display overrides for curves
                            kids = cmds.listRelatives(
                                "QC_head_GRP", c=True,
                                type="transform", f=True) or []
                            for k in kids:
                                _qc_set_curve_display(
                                    k, color_index=17,
                                    line_width=3.0)

                            # Apply useBackground shader to meshes
                            # so they occlude the crown via depth
                            # but render as transparent.
                            crown_bg_shader = cmds.shadingNode(
                                "useBackground", asShader=True,
                                name="mme_crownBg_mtl")
                            crown_bg_sg = cmds.sets(
                                renderable=True,
                                noSurfaceShader=True,
                                empty=True,
                                name="mme_crownBg_SG")
                            cmds.connectAttr(
                                "{}.outColor".format(
                                    crown_bg_shader),
                                "{}.surfaceShader".format(
                                    crown_bg_sg),
                                force=True)
                            crown_orig_shading = {}
                            if mm_transforms:
                                for mt in mm_transforms:
                                    try:
                                        sgs = cmds.listConnections(
                                            mt,
                                            type="shadingEngine"
                                        ) or []
                                        if sgs:
                                            crown_orig_shading[
                                                mt] = sgs[0]
                                    except Exception:
                                        pass
                                cmds.select(
                                    mm_transforms, replace=True)
                                cmds.hyperShade(
                                    assign=crown_bg_shader)
                                cmds.select(clear=True)

                            cmds.modelEditor(
                                model_panel, edit=True,
                                imagePlane=False,
                                polymeshes=True,
                                nurbsSurfaces=False,
                                subdivSurfaces=False,
                                nurbsCurves=True)
                            # Scrub to start frame so constraints
                            # evaluate before first frame render
                            cmds.currentTime(
                                int(start_frame), edit=True)
                            cmds.ogs(reset=True)
                            cmds.refresh(force=True)
                            cmds.playblast(
                                filename=crown_path,
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
                                widthHeight=[pb_width, pb_height],
                            )
                            has_crown_pass = True

                            # Restore original shading and cleanup
                            for mt, sg in crown_orig_shading.items():
                                try:
                                    if (cmds.objExists(mt)
                                            and cmds.objExists(sg)):
                                        cmds.sets(
                                            mt, edit=True,
                                            forceElement=sg)
                                except Exception:
                                    pass
                            for node in (crown_bg_sg,
                                         crown_bg_shader):
                                try:
                                    if cmds.objExists(node):
                                        cmds.delete(node)
                                except Exception:
                                    pass

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
            # Skip if the composite path already saved/set displayLights
            # (original_display_lights is not None), to avoid overwriting
            # the correct saved value.
            original_flat_lighting = None
            if (not raw_playblast and model_panel
                    and original_display_lights is None):
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

                    c_crown_dir = None
                    c_crown_base = None
                    if has_crown_pass:
                        c_crown_dir = os.path.join(
                            composite_tmp_dir, "crown")
                        c_crown_base = os.path.basename(
                            composite_matte_path)

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
                            png_output=True,
                            show_hud=show_hud,
                            focal_length=hud_focal_length,
                            resolution=(pb_width, pb_height),
                            crown_dir=c_crown_dir,
                            crown_base=c_crown_base)
                    elif mp4_mode:
                        encode_ok = self._encode_composite(
                            plate_dir, plate_base,
                            color_dir, color_base,
                            matte_dir, matte_base,
                            start_frame, mp4_output,
                            opacity=opacity_01,
                            show_hud=show_hud,
                            focal_length=hud_focal_length,
                            resolution=(pb_width, pb_height),
                            crown_dir=c_crown_dir,
                            crown_base=c_crown_base)
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
                            opacity=opacity_01,
                            show_hud=show_hud,
                            focal_length=hud_focal_length,
                            resolution=(pb_width, pb_height),
                            crown_dir=c_crown_dir,
                            crown_base=c_crown_base)

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
                else:
                    # Camera Track: render to temp PNGs, then
                    # encode via ffmpeg with HUD metadata overlay.
                    import tempfile as _tf
                    ct_tmp = _tf.mkdtemp(prefix="ExportGenie_ct_")
                    ct_tmp_base = "ct_tmp_frame"
                    ct_tmp_file = os.path.join(ct_tmp, ct_tmp_base)
                    self.log("Rendering...")
                    cmds.playblast(
                        filename=ct_tmp_file,
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
                        widthHeight=[pb_width, pb_height],
                    )
                    if mp4_mode:
                        encode_ok = self._encode_mp4(
                            ct_tmp, ct_tmp_base, start_frame,
                            mp4_output,
                            show_hud=show_hud,
                            focal_length=hud_focal_length,
                            resolution=(pb_width, pb_height))
                    elif png_mode:
                        # Burn HUD into PNG sequence via ffmpeg
                        out_dir = os.path.dirname(file_path)
                        if not os.path.exists(out_dir):
                            os.makedirs(out_dir)
                        out_base = os.path.basename(file_path)
                        out_pattern = os.path.join(
                            out_dir,
                            out_base + ".%04d.png")
                        hud_filters = None
                        if show_hud and self._has_drawtext():
                            hud_f = self._build_hud_drawtext(
                                start_frame, hud_focal_length,
                                resolution=(pb_width, pb_height))
                            hud_filters = hud_f.replace(
                                "[pre_hud]", "").replace(
                                "[out]", "")
                        ffmpeg_path = self._find_ffmpeg()
                        if ffmpeg_path and hud_filters:
                            in_pattern = os.path.join(
                                ct_tmp,
                                ct_tmp_base + ".%04d.png")
                            cmd = [
                                ffmpeg_path, "-y",
                                "-framerate", str(self._get_fps()),
                                "-start_number",
                                str(int(start_frame)),
                                "-i", in_pattern,
                            ]
                            if sys.platform == "win32":
                                import tempfile as _tf2
                                fd, sp = _tf2.mkstemp(
                                    suffix=".txt",
                                    prefix="ffmpeg_vf_")
                                try:
                                    with os.fdopen(fd, "w") as fh:
                                        fh.write(hud_filters)
                                    cmd.extend([
                                        "-filter_script:v", sp])
                                    cmd.extend([
                                        "-start_number",
                                        str(int(start_frame)),
                                        out_pattern])
                                    subprocess.run(
                                        cmd,
                                        stdin=subprocess.DEVNULL,
                                        capture_output=True,
                                        text=True,
                                        timeout=600,
                                        creationflags=getattr(
                                            subprocess,
                                            "CREATE_NO_WINDOW",
                                            0))
                                finally:
                                    try:
                                        os.remove(sp)
                                    except Exception:
                                        pass
                            else:
                                cmd.extend(["-vf", hud_filters])
                                cmd.extend([
                                    "-start_number",
                                    str(int(start_frame)),
                                    out_pattern])
                                subprocess.run(
                                    cmd,
                                    stdin=subprocess.DEVNULL,
                                    capture_output=True,
                                    text=True,
                                    timeout=600,
                                    creationflags=getattr(
                                        subprocess,
                                        "CREATE_NO_WINDOW", 0))
                            encode_ok = True
                        else:
                            # No ffmpeg or no HUD — just copy PNGs
                            import shutil
                            out_dir2 = os.path.dirname(file_path)
                            if not os.path.exists(out_dir2):
                                os.makedirs(out_dir2)
                            for f in sorted(os.listdir(ct_tmp)):
                                if f.endswith(".png"):
                                    src = os.path.join(ct_tmp, f)
                                    dst_name = f.replace(
                                        ct_tmp_base,
                                        os.path.basename(file_path))
                                    dst = os.path.join(
                                        out_dir2, dst_name)
                                    shutil.copy2(src, dst)
                            encode_ok = True
                    else:
                        # .mov / default — encode to mp4 via ffmpeg
                        ct_output = file_path
                        if sys.platform == "darwin":
                            ct_output = os.path.splitext(
                                file_path)[0] + ".mp4"
                        encode_ok = self._encode_mp4(
                            ct_tmp, ct_tmp_base, start_frame,
                            ct_output,
                            show_hud=show_hud,
                            focal_length=hud_focal_length,
                            resolution=(pb_width, pb_height))
                    if encode_ok:
                        self._cleanup_temp_pngs(ct_tmp)
                    else:
                        self.log(
                            "Encode failed — temp PNGs kept at "
                            "{}".format(ct_tmp))
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
                if original_shadows is not None and model_panel:
                    try:
                        cmds.modelEditor(
                            model_panel, edit=True,
                            shadows=original_shadows)
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
                # Delete auto-created QC crown
                if auto_qc_crown and cmds.objExists(auto_qc_crown):
                    try:
                        cmds.delete(auto_qc_crown)
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
        current_use_vt = None
        try:
            current_otn = cmds.colorManagementPrefs(
                query=True, outputTransformName=True,
                outputTarget="playblast")
        except Exception:
            pass
        try:
            current_use_vt = cmds.colorManagementPrefs(
                query=True, outputUseViewTransform=True,
                outputTarget="playblast")
        except Exception:
            pass
        sys.stderr.write(
            "[ExportGenie] Playblast color: current='{}', "
            "useViewTransform={}, target='{}'\n".format(
                current_otn, current_use_vt, chosen_name))

        if current_otn == chosen_name and not current_use_vt:
            return

        # --- Apply the setting ---
        # Disable "Use View Transform" for playblast so Maya uses
        # our explicit outputTransformName instead of inheriting
        # whatever the viewport is set to.
        self.log("Setting color management to Raw...")
        try:
            cmds.colorManagementPrefs(
                edit=True,
                outputUseViewTransform=False,
                outputTarget="playblast")
        except Exception as exc:
            sys.stderr.write(
                "[ExportGenie] outputUseViewTransform "
                "failed: {}\n".format(exc))
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

        h_aperture_inches = cmds.getAttr(cam_shape + ".horizontalFilmAperture")
        h_aperture_mm = h_aperture_inches * 25.4

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
        jsx.append("var zoomArray = new Array();")

        for frame in range(int(start_frame), int(end_frame) + 1):
            cmds.currentTime(frame)
            pos, rot, _ = self._world_matrix_to_ae(
                camera, ae_scale, comp_cx, comp_cy
            )

            focal_length = cmds.getAttr(cam_shape + ".focalLength")
            ae_zoom = focal_length * comp_width / h_aperture_mm

            time_sec = (frame - start_frame + 1) / fps

            jsx.append("timesArray.push({:.10f});".format(time_sec))
            jsx.append("posArray.push([{:.10f}, {:.10f}, {:.10f}]);".format(
                pos[0], pos[1], pos[2]))
            jsx.append("rotXArray.push({:.10f});".format(rot[0]))
            jsx.append("rotYArray.push({:.10f});".format(rot[1]))
            jsx.append("rotZArray.push({:.10f});".format(rot[2]))
            jsx.append("zoomArray.push({:.10f});".format(ae_zoom))

        jsx.append("")
        jsx.append("{v}.position.setValuesAtTimes(timesArray, posArray);".format(v=layer_var))
        jsx.append("{v}.rotationX.setValuesAtTimes(timesArray, rotXArray);".format(v=layer_var))
        jsx.append("{v}.rotationY.setValuesAtTimes(timesArray, rotYArray);".format(v=layer_var))
        jsx.append("{v}.rotationZ.setValuesAtTimes(timesArray, rotZArray);".format(v=layer_var))
        jsx.append("{v}.zoom.setValuesAtTimes(timesArray, zoomArray);".format(v=layer_var))
        jsx.append("")
        return jsx

    # --- Mesh Warp Preset Helpers (STMap → AE .ffx) ---

    @staticmethod
    def _read_stmap_pixels(stmap_path):
        """Read a 32-bit EXR STMap and return (width, height, pixels).

        Uses maya.api.OpenMaya.MImage to load the EXR as float data.
        Returns the raw float buffer as a ctypes array of
        (width * height * 4) floats (RGBA layout).
        """
        from maya.api.OpenMaya import MImage
        img = MImage()
        img.readFromFile(stmap_path, MImage.kFloat)
        w, h = img.getSize()
        ptr = img.floatPixels()
        num_floats = w * h * 4
        arr = (ctypes.c_float * num_floats).from_address(ptr)
        # Copy out — the MImage buffer lifetime is tied to img
        pixels = list(arr)
        return w, h, pixels

    @staticmethod
    def _sample_stmap(pixels, img_w, img_h, norm_x, norm_y):
        """Sample the STMap at normalised (0-1) coordinates.

        Returns (u, v) from the R and G channels using bilinear
        interpolation.  Coordinates outside [0,1] are clamped.
        """
        fx = max(0.0, min(norm_x * (img_w - 1), img_w - 1.001))
        fy = max(0.0, min(norm_y * (img_h - 1), img_h - 1.001))
        ix = int(fx)
        iy = int(fy)
        dx = fx - ix
        dy = fy - iy
        ix1 = min(ix + 1, img_w - 1)
        iy1 = min(iy + 1, img_h - 1)

        def _px(px_x, px_y):
            # STMap images store bottom-to-top; MImage loads top-to-top,
            # so row 0 = top of image.  Flip Y for bottom-origin STMaps.
            flipped_y = (img_h - 1) - px_y
            idx = (flipped_y * img_w + px_x) * 4
            return pixels[idx], pixels[idx + 1]  # R, G

        r00, g00 = _px(ix, iy)
        r10, g10 = _px(ix1, iy)
        r01, g01 = _px(ix, iy1)
        r11, g11 = _px(ix1, iy1)
        u = (r00 * (1 - dx) * (1 - dy) + r10 * dx * (1 - dy) +
             r01 * (1 - dx) * dy + r11 * dx * dy)
        v = (g00 * (1 - dx) * (1 - dy) + g10 * dx * (1 - dy) +
             g01 * (1 - dx) * dy + g11 * dx * dy)
        return u, v

    @staticmethod
    def _build_stmap_grid(pixels, img_w, img_h, grid_res,
                          overscan_x=0.0, overscan_y=0.0):
        """Sample an (grid_res+1) x (grid_res+1) grid from an STMap.

        Returns a 2D list where each entry is:
            [src_x, src_y, dst_x, dst_y, sample_x, sample_y]
        src/dst are in unit-space [0,1].  sample_x/y are the actual
        STMap coordinates used (may extend beyond [0,1] with overscan)
        and are stored for Jacobian computation.
        """
        grid = []
        for y in range(grid_res + 1):
            row = []
            for x in range(grid_res + 1):
                src_x = x / float(grid_res)
                src_y = y / float(grid_res)
                if overscan_x or overscan_y:
                    sample_x = -overscan_x + src_x * (overscan_x * 2 + 1.0)
                    sample_y = -overscan_y + src_y * (overscan_y * 2 + 1.0)
                else:
                    sample_x = src_x
                    sample_y = src_y
                dst_x, dst_y = Exporter._sample_stmap(
                    pixels, img_w, img_h, sample_x, sample_y)
                if overscan_x or overscan_y:
                    dst_x = (dst_x + overscan_x) / (overscan_x * 2 + 1.0)
                    dst_y = (dst_y + overscan_y) / (overscan_y * 2 + 1.0)
                row.append([src_x, src_y, dst_x, dst_y, sample_x, sample_y])
            grid.append(row)
        return grid

    @staticmethod
    def _compute_jacobian_from_stmap(pixels, img_w, img_h, norm_x, norm_y):
        """Approximate the 2x2 Jacobian of the STMap at (norm_x, norm_y).

        Uses finite differences with a small epsilon.
        Returns [[du/dx, du/dy], [dv/dx, dv/dy]].
        """
        eps = 0.5 / max(img_w, img_h)
        u_px, v_px = Exporter._sample_stmap(
            pixels, img_w, img_h, norm_x + eps, norm_y)
        u_mx, v_mx = Exporter._sample_stmap(
            pixels, img_w, img_h, norm_x - eps, norm_y)
        u_py, v_py = Exporter._sample_stmap(
            pixels, img_w, img_h, norm_x, norm_y + eps)
        u_my, v_my = Exporter._sample_stmap(
            pixels, img_w, img_h, norm_x, norm_y - eps)
        denom = 2.0 * eps
        return [
            [(u_px - u_mx) / denom, (u_py - u_my) / denom],
            [(v_px - v_mx) / denom, (v_py - v_my) / denom],
        ]

    @staticmethod
    def _invert_2x2(m):
        """Invert a 2x2 matrix [[a,b],[c,d]]. Returns identity on failure."""
        det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
        if abs(det) < 1e-12:
            return [[1, 0], [0, 1]]
        inv_det = 1.0 / det
        return [
            [m[1][1] * inv_det, -m[0][1] * inv_det],
            [-m[1][0] * inv_det, m[0][0] * inv_det],
        ]

    @staticmethod
    def _mat2x2_mul_vec(m, v):
        """Multiply 2x2 matrix by 2-vector."""
        return [
            m[0][0] * v[0] + m[0][1] * v[1],
            m[1][0] * v[0] + m[1][1] * v[1],
        ]

    # --- .ffx Binary Preset Writer ---

    @staticmethod
    def _ae_fib(frames):
        """Compute Fibonacci-based timing values required by AE preset format."""
        v1, v2 = 0, 1
        while 4 * (v2 - 1) < int(frames):
            v1, v2 = v2, v1 + v2
        return v2 - 1, 4 * (v2 - 1)

    @staticmethod
    def _ffx_main_chunks():
        """Return the static .ffx skeleton blob (reverse-engineered from AE)."""
        return bytearray([0x52,0x49,0x46,0x58,0x00,0x00,0x40,0x94,0x46,0x61,0x46,0x58,0x68,0x65,0x61,0x64,0x00,0x00,0x00,0x10,0x00,0x00,0x00,0x03,0x00,0x00,0x00,0x4a,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x40,0x70,0x62,0x65,0x73,0x63,0x62,0x65,0x73,0x6f,0x00,0x00,0x00,0x38,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x64,0x00,0x00,0x19,0x00,0x00,0x00,0x00,0x00,0x00,0x0a,0x00,0x04,0x2b,0x0a,0x00,0x04,0x2b,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xff,0xff,0xff,0xff,0x4c,0x49,0x53,0x54,0x00,0x00,0x00,0xac,0x74,0x64,0x73,0x70,0x74,0x64,0x6f,0x74,0x00,0x00,0x00,0x04,0xff,0xff,0xff,0xff,0x74,0x64,0x70,0x6c,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x02,0x4c,0x49,0x53,0x54,0x00,0x00,0x00,0x40,0x74,0x64,0x73,0x69,0x74,0x64,0x69,0x78,0x00,0x00,0x00,0x04,0xff,0xff,0xff,0xff,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x45,0x66,0x66,0x65,0x63,0x74,0x20,0x50,0x61,0x72,0x61,0x64,0x65,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x00,0x40,0x74,0x64,0x73,0x69,0x74,0x64,0x69,0x78,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x00,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x73,0x6e,0x00,0x00,0x00,0x0a,0x4d,0x65,0x73,0x68,0x20,0x57,0x61,0x72,0x70,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x00,0x64,0x74,0x64,0x73,0x70,0x74,0x64,0x6f,0x74,0x00,0x00,0x00,0x04,0xff,0xff,0xff,0xff,0x74,0x64,0x70,0x6c,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x01,0x4c,0x49,0x53,0x54,0x00,0x00,0x00,0x40,0x74,0x64,0x73,0x69,0x74,0x64,0x69,0x78,0x00,0x00,0x00,0x04,0xff,0xff,0xff,0xff,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x45,0x6e,0x64,0x20,0x6f,0x66,0x20,0x70,0x61,0x74,0x68,0x20,0x73,0x65,0x6e,0x74,0x69,0x6e,0x65,0x6c,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x3e,0xf2,0x73,0x73,0x70,0x63,0x66,0x6e,0x61,0x6d,0x00,0x00,0x00,0x30,0x4d,0x65,0x73,0x68,0x20,0x57,0x61,0x72,0x70,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x04,0xc8,0x70,0x61,0x72,0x54,0x70,0x61,0x72,0x6e,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x05,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x2d,0x30,0x30,0x30,0x30,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x70,0x61,0x72,0x64,0x00,0x00,0x00,0x94,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0d,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xff,0xff,0xff,0xff,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x2d,0x30,0x30,0x30,0x31,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x70,0x61,0x72,0x64,0x00,0x00,0x00,0x94,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x52,0x6f,0x77,0x73,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x07,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x1f,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x1f,0x00,0x00,0x00,0x07,0x00,0x00,0x00,0x00,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x2d,0x30,0x30,0x30,0x32,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x70,0x61,0x72,0x64,0x00,0x00,0x00,0x94,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x43,0x6f,0x6c,0x75,0x6d,0x6e,0x73,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x07,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x1f,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x1f,0x00,0x00,0x00,0x07,0x00,0x00,0x00,0x00,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x2d,0x30,0x30,0x30,0x35,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x70,0x61,0x72,0x64,0x00,0x00,0x00,0x94,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x51,0x75,0x61,0x6c,0x69,0x74,0x79,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x08,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x0a,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x0a,0x00,0x00,0x00,0x08,0x00,0x00,0x00,0x00,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x2d,0x30,0x30,0x30,0x34,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x70,0x61,0x72,0x64,0x00,0x00,0x00,0x94,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x01,0x06,0x00,0x28,0x00,0x00,0x00,0x0b,0x44,0x69,0x73,0x74,0x6f,0x72,0x74,0x69,0x6f,0x6e,0x20,0x4d,0x65,0x73,0x68,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x20,0x00,0x00,0x00,0x00,0xd2,0x04,0x00,0x00,0x30,0x6a,0xc3,0x30,0x50,0x98,0x1f,0x23,0xef,0xbe,0xad,0xde,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x61,0x52,0x62,0x70,0x00,0x00,0x00,0xb4,0x00,0x00,0x00,0x02,0x00,0x00,0x00,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x0d,0x0d,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x3e,0xaa,0xaa,0x9f,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x3e,0xaa,0xaa,0x9f,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0x80,0x00,0x00,0x3e,0xaa,0xaa,0x9f,0x3f,0x2a,0xaa,0x9f,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0x2a,0xaa,0x9f,0x3e,0xaa,0xaa,0x9f,0x3f,0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0x80,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0x80,0x00,0x00,0x3f,0x80,0x00,0x00,0x3f,0x80,0x00,0x00,0x3f,0x80,0x00,0x00,0x3f,0x2a,0xaa,0x9f,0x3f,0x80,0x00,0x00,0x3f,0x80,0x00,0x00,0x3f,0x80,0x00,0x00,0x3f,0x80,0x00,0x00,0x3f,0x2a,0xaa,0x9f,0x3f,0x80,0x00,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x39,0xde,0x74,0x64,0x67,0x70,0x74,0x64,0x73,0x62,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x09,0x74,0x64,0x73,0x6e,0x00,0x00,0x00,0x0a,0x4d,0x65,0x73,0x68,0x20,0x57,0x61,0x72,0x70,0x00,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x2d,0x30,0x30,0x30,0x30,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x00,0xda,0x74,0x64,0x62,0x73,0x74,0x64,0x73,0x62,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x03,0x74,0x64,0x73,0x6e,0x00,0x00,0x00,0x01,0x00,0x00,0x74,0x64,0x62,0x34,0x00,0x00,0x00,0x7c,0xdb,0x99,0x00,0x01,0x00,0x01,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x64,0x00,0x3f,0x1a,0x36,0xe2,0xeb,0x1c,0x43,0x2d,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x04,0x04,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x30,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x63,0x64,0x61,0x74,0x00,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x70,0x69,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x0d,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x2d,0x30,0x30,0x30,0x31,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x00,0xf2,0x74,0x64,0x62,0x73,0x74,0x64,0x73,0x62,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x01,0x74,0x64,0x73,0x6e,0x00,0x00,0x00,0x05,0x52,0x6f,0x77,0x73,0x00,0x00,0x74,0x64,0x62,0x34,0x00,0x00,0x00,0x7c,0xdb,0x99,0x00,0x01,0x00,0x01,0x00,0x00,0xff,0xff,0xff,0xff,0x00,0x00,0x64,0x00,0x3f,0x1a,0x36,0xe2,0xeb,0x1c,0x43,0x2d,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x04,0x04,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x63,0x64,0x61,0x74,0x00,0x00,0x00,0x28,0x40,0x1c,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x75,0x6d,0x00,0x00,0x00,0x08,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x75,0x4d,0x00,0x00,0x00,0x08,0x40,0x3f,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x2d,0x30,0x30,0x30,0x32,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x00,0xf4,0x74,0x64,0x62,0x73,0x74,0x64,0x73,0x62,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x01,0x74,0x64,0x73,0x6e,0x00,0x00,0x00,0x08,0x43,0x6f,0x6c,0x75,0x6d,0x6e,0x73,0x00,0x74,0x64,0x62,0x34,0x00,0x00,0x00,0x7c,0xdb,0x99,0x00,0x01,0x00,0x01,0x00,0x00,0xff,0xff,0xff,0xff,0x00,0x00,0x64,0x00,0x3f,0x1a,0x36,0xe2,0xeb,0x1c,0x43,0x2d,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x04,0x04,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x63,0x64,0x61,0x74,0x00,0x00,0x00,0x28,0x40,0x1c,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x75,0x6d,0x00,0x00,0x00,0x08,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x75,0x4d,0x00,0x00,0x00,0x08,0x40,0x3f,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x2d,0x30,0x30,0x30,0x35,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x00,0xf4,0x74,0x64,0x62,0x73,0x74,0x64,0x73,0x62,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x01,0x74,0x64,0x73,0x6e,0x00,0x00,0x00,0x08,0x51,0x75,0x61,0x6c,0x69,0x74,0x79,0x00,0x74,0x64,0x62,0x34,0x00,0x00,0x00,0x7c,0xdb,0x99,0x00,0x01,0x00,0x01,0x00,0x00,0xff,0xff,0xff,0xff,0x00,0x00,0x64,0x00,0x3f,0x1a,0x36,0xe2,0xeb,0x1c,0x43,0x2d,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x04,0x04,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x63,0x64,0x61,0x74,0x00,0x00,0x00,0x28,0x40,0x20,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x75,0x6d,0x00,0x00,0x00,0x08,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x75,0x4d,0x00,0x00,0x00,0x08,0x40,0x24,0x00,0x00,0x00,0x00,0x00,0x00,0x74,0x64,0x6d,0x6e,0x00,0x00,0x00,0x28,0x41,0x44,0x42,0x45,0x20,0x4d,0x45,0x53,0x48,0x20,0x57,0x41,0x52,0x50,0x2d,0x30,0x30,0x30,0x34,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x4c,0x49,0x53,0x54,0x00,0x00,0x02,0x28,0x74,0x64,0x62,0x73,0x74,0x64,0x73,0x62,0x00,0x00,0x00,0x04,0x00,0x00,0x00,0x01,0x74,0x64,0x73,0x6e,0x00,0x00,0x00,0x10,0x44,0x69,0x73,0x74,0x6f,0x72,0x74,0x69,0x6f,0x6e,0x20,0x4d,0x65,0x73,0x68,0x00,0x74,0x64,0x62,0x34,0x00,0x00,0x00,0x7c,0xdb,0x99,0x00,0x01,0x00,0x06,0x00,0x01,0x00,0x06,0x00,0x07,0x00,0x00,0x64,0x00,0x3f,0x1a,0x36,0xe2,0xeb,0x1c,0x43,0x2d,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x3f,0xf0,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x00,0x04,0x01,0x00,0x00,0x00,0xa4,0x96,0x68,0x01,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])

    @staticmethod
    def _write_mesh_warp_ffx(filename, grid_res_x, grid_res_y, grid,
                             pixels, img_w, img_h, invert_jacobian,
                             fps, frame_offset):
        """Write a single .ffx mesh warp preset file.

        Args:
            filename: Output .ffx path.
            grid_res_x/y: Grid resolution (e.g. 11).
            grid: 2D list from _build_stmap_grid().
            pixels: Raw STMap float pixel buffer.
            img_w/h: STMap image dimensions.
            invert_jacobian: True for apply-distortion preset.
            fps: Scene frame rate.
            frame_offset: Maya start frame number, used for AE timecode.
        """
        frames = 1  # Static distortion — single keyframe
        t_width = 1.0 / float(grid_res_x) / 3.0
        t_height = 1.0 / float(grid_res_y) / 3.0

        # Build mesh point data (aRbs container with one aRbp sub-chunk)
        aRbs_chunk = bytearray(b'aRbs')

        # Single frame — one aRbp header
        rows = grid_res_y + 1
        cols = grid_res_x + 1
        s = rows * cols * 4 * 10 + 12 + 8
        aRbp = bytearray(b'aRbp')
        aRbp += struct.pack(">I", s)
        aRbp += struct.pack(">I", rows)
        aRbp += struct.pack(">I", cols)
        aRbp += bytearray([0x00, 0x00, 0x00, 0x00,
                           0x00, 0x00, 0x00, 0x00,
                           0x00, 0x00, 0x0D, 0x0D])
        aRbs_chunk += aRbp

        # Iterate grid in reversed Y order (top-to-bottom in AE space)
        for y in reversed(range(grid_res_y + 1)):
            for x in range(grid_res_x + 1):
                # Use the actual STMap sample coordinates for Jacobian
                # (these may extend beyond [0,1] when overscan is active)
                jac_x = grid[y][x][4]
                jac_y = grid[y][x][5]

                # Compute Jacobian from STMap via finite differences
                jmat = Exporter._compute_jacobian_from_stmap(
                    pixels, img_w, img_h, jac_x, jac_y)
                if invert_jacobian:
                    jmat = Exporter._invert_2x2(jmat)

                # Cardinal tangent vectors
                r_vec = [t_width, 0.0]
                l_vec = [-t_width, 0.0]
                o_vec = [0.0, t_height]
                u_vec = [0.0, -t_height]

                # Transform through Jacobian
                r_t = Exporter._mat2x2_mul_vec(jmat, r_vec)
                l_t = Exporter._mat2x2_mul_vec(jmat, l_vec)
                o_t = Exporter._mat2x2_mul_vec(jmat, o_vec)
                u_t = Exporter._mat2x2_mul_vec(jmat, u_vec)

                # Destination point with Y-flip for AE coordinate system
                pointx = grid[y][x][2]
                pointy = 1.0 - grid[y][x][3]

                # Tangent handle positions
                ta_rx = pointx + r_t[0]
                ta_ry = pointy - r_t[1]
                ta_lx = pointx + l_t[0]
                ta_ly = pointy - l_t[1]
                ta_ox = pointx + o_t[0]
                ta_oy = pointy - o_t[1]
                ta_ux = pointx + u_t[0]
                ta_uy = pointy - u_t[1]

                # Write 5 float pairs: anchor, top, right, bottom, left
                aRbs_chunk += struct.pack(">ff", pointx, pointy)
                aRbs_chunk += struct.pack(">ff", ta_ox, ta_oy)
                aRbs_chunk += struct.pack(">ff", ta_rx, ta_ry)
                aRbs_chunk += struct.pack(">ff", ta_ux, ta_uy)
                aRbs_chunk += struct.pack(">ff", ta_lx, ta_ly)

        # Build timing chunks (single keyframe)
        list_chunk = bytearray([
            0x6C, 0x69, 0x73, 0x74, 0x6C, 0x68, 0x64, 0x33,
            0x00, 0x00, 0x00, 0x34, 0x00, 0xD0, 0x0B, 0xEE,
            0x33, 0x04, 0x1D, 0x18, 0x00, 0x00, 0x00, 0x03,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x3C,
            0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x01,
            0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x94, 0xE7, 0xEC, 0x01,
            0xD4, 0xE8, 0xEC, 0x01, 0x0C, 0xAF, 0xEB, 0x01,
        ])
        list_chunk[20:24] = struct.pack(">I", frames)

        # ldat chunk — one 60-byte keyframe record
        fps_factor = 100.0 / fps
        ldat = bytearray(b'ldat')
        ldat += struct.pack(">I", frames * 60)
        timecode = int(frame_offset * fps_factor) << 8
        ldat += struct.pack(">I", timecode)
        ldat += struct.pack(">I", 0x01010001)
        ldat += struct.pack(">I", 2)
        ldat += struct.pack(">I", 0)
        ldat += struct.pack(">d", 0.0)
        ldat += struct.pack(">d", 1.0)
        ldat += struct.pack(">d", 1.0)
        ldat += struct.pack(">d", 1.0)
        ldat += struct.pack(">d", 1.0)
        ldat += struct.pack(">f", 0.0)

        # Assemble LIST chunks
        def _make_list(chunks):
            data = bytearray(b'LIST')
            total = sum(len(c) for c in chunks)
            data += struct.pack(">I", total)
            for c in chunks:
                data += c
            return data

        LIST_timing = _make_list([list_chunk, ldat])
        LIST_mesh = _make_list([aRbs_chunk])
        end_chunk = bytearray([
            0x74, 0x64, 0x6D, 0x6E, 0x00, 0x00, 0x00, 0x28,
            0x41, 0x44, 0x42, 0x45, 0x20, 0x47, 0x72, 0x6F,
            0x75, 0x70, 0x20, 0x45, 0x6E, 0x64, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        ])

        # Get main skeleton and patch it
        a = Exporter._ffx_main_chunks()
        a += LIST_timing
        a += LIST_mesh
        a += end_chunk

        lt = len(LIST_timing)
        lm = len(LIST_mesh) + len(end_chunk)
        a[4:8] = struct.pack(">I", 3152 + lt + lm)
        a[40:44] = struct.pack(">I", 3116 + lt + lm)
        a[422:426] = struct.pack(">I", 2734 + lt + lm)
        a[1722:1726] = struct.pack(">I", 1434 + lt + lm)
        a[2984:2988] = struct.pack(">I", 172 + lt)
        a[826:830] = struct.pack(">I", grid_res_x)
        a[1030:1034] = struct.pack(">I", grid_res_y)

        lup = {7: 28, 11: 38, 13: 42, 19: 51}
        a[2261] = lup[grid_res_x]
        a[2561] = lup[grid_res_y]

        v1, v2 = Exporter._ae_fib(frames)
        a[3192:3196] = struct.pack(">I", int(v1))
        a[3208:3212] = struct.pack(">I", int(v2))

        with open(filename, "wb") as f:
            f.write(a)

    # --- JSX Mesh Warp Adjustment Layer ---

    @staticmethod
    def _jsx_mesh_warp_adjustment(ffx_filename, label, duration):
        """Generate JSX lines to create an adjustment layer with a mesh
        warp preset applied.  The layer is placed at the top of the comp.

        Args:
            ffx_filename: Basename of the .ffx file (resolved relative
                to the JSX script's directory).
            label: Display name for the adjustment layer.
            duration: Comp duration in seconds.
        """
        jsx = []
        safe_var = re.sub(r'[^A-Za-z0-9_]', '_', label)
        jsx_ffx = ffx_filename.replace("\\", "/")

        jsx.append("// Mesh Warp: {}".format(label))
        jsx.append("var _scriptDir_{v} = (new File($.fileName)).parent;".format(
            v=safe_var))
        jsx.append(
            "var ffxFile_{v} = new File("
            "_scriptDir_{v}.fsName + '/' + '{f}');".format(
                v=safe_var, f=jsx_ffx))
        jsx.append(
            "if (!ffxFile_{v}.exists) ffxFile_{v} = File.openDialog("
            "'Locate {f}', '*.ffx', false);".format(v=safe_var, f=jsx_ffx))
        jsx.append(
            "if (ffxFile_{v}) {{".format(v=safe_var))
        jsx.append(
            "    var adj_{v} = comp.layers.addSolid("
            "[0,0,0], '{lbl}', comp.width, comp.height, 1.0, {dur});".format(
                v=safe_var, lbl=label, dur=duration))
        jsx.append(
            "    adj_{v}.adjustmentLayer = true;".format(v=safe_var))
        jsx.append(
            "    adj_{v}.moveToBeginning();".format(v=safe_var))
        jsx.append(
            "    adj_{v}.applyPreset(ffxFile_{v});".format(v=safe_var))
        jsx.append("}")
        jsx.append("")
        return jsx

    # --- Mesh Warp Orchestrator ---

    def _export_mesh_warp_presets(self, ae_dir, scene_base, version_str,
                                  stmap_undistort, stmap_redistort,
                                  fps, start_frame, duration):
        """Read STMaps, write .ffx presets, return JSX lines.

        Called from export_jsx() when STMap paths are provided.
        Returns a list of JSX lines to insert before the footer.
        """
        grid_res = 11
        jsx_lines = []

        for label, stmap_path, invert_jac in [
            ("Undistort", stmap_undistort, False),
            ("Redistort", stmap_redistort, True),
        ]:
            if not stmap_path:
                continue
            self._log("Reading STMap: {}".format(
                os.path.basename(stmap_path)))
            img_w, img_h, pixels = Exporter._read_stmap_pixels(stmap_path)

            # Detect overscan from redistort STMap edge values
            overscan_x = 0.0
            overscan_y = 0.0
            if invert_jac:
                # Sample corners — if UV extends beyond [0,1] there is overscan
                u0, v0 = Exporter._sample_stmap(
                    pixels, img_w, img_h, 0.0, 0.0)
                u1, v1 = Exporter._sample_stmap(
                    pixels, img_w, img_h, 1.0, 1.0)
                overscan_x = max(0.0, -min(u0, 0.0), max(u1 - 1.0, 0.0))
                overscan_y = max(0.0, -min(v0, 0.0), max(v1 - 1.0, 0.0))

            grid = Exporter._build_stmap_grid(
                pixels, img_w, img_h, grid_res,
                overscan_x, overscan_y)

            tag = "remove" if label == "Undistort" else "apply"
            ffx_name = "{}_{}_meshwarp_{}.ffx".format(
                scene_base, tag, version_str)
            ffx_path = os.path.join(ae_dir, ffx_name)

            self._log("Writing .ffx preset: {}".format(ffx_name))
            Exporter._write_mesh_warp_ffx(
                ffx_path, grid_res, grid_res, grid,
                pixels, img_w, img_h, invert_jac,
                fps, int(start_frame))

            jsx_lines.extend(Exporter._jsx_mesh_warp_adjustment(
                ffx_name, "Lens {}".format(label), duration))

        return jsx_lines

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
        jsx.append("bkgLayer.startTime = 0;")
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

        # Check for any animation source: direct animCurves,
        # constraints, or other driven connections on TRS.
        is_animated = bool(
            cmds.listConnections(geo_child, type="animCurve"))
        if not is_animated:
            for attr in ("tx", "ty", "tz", "rx", "ry", "rz",
                         "sx", "sy", "sz"):
                conns = cmds.listConnections(
                    "{}.{}".format(geo_child, attr),
                    source=True, destination=False) or []
                if conns:
                    is_animated = True
                    break

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

                time_sec = (frame - start_frame) / fps

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
            cmds.listConnections(locator_node, type="animCurve"))
        if not is_animated:
            for attr in ("tx", "ty", "tz", "rx", "ry", "rz",
                         "sx", "sy", "sz"):
                conns = cmds.listConnections(
                    "{}.{}".format(locator_node, attr),
                    source=True, destination=False) or []
                if conns:
                    is_animated = True
                    break

        if is_animated:
            jsx.append("var timesArray = new Array();")
            jsx.append("var posArray = new Array();")

            for frame in range(int(start_frame), int(end_frame) + 1):
                cmds.currentTime(frame)
                pos, _, _ = self._world_matrix_to_ae(
                    locator_node, ae_scale, comp_cx, comp_cy
                )
                time_sec = (frame - start_frame) / fps

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

    def export_jsx(self, jsx_path, obj_paths, camera, geo_children,
                   start_frame, end_frame,
                   stmap_undistort="", stmap_redistort=""):
        """Export After Effects JSX + OBJ files.

        Args:
            jsx_path: Output .jsx file path.
            obj_paths: dict of {geo_child_name: obj_file_path}.
            camera: Maya camera transform (or None).
            geo_children: list of pre-filtered geo child transforms.
            start_frame: First frame.
            end_frame: Last frame.
            stmap_undistort: Path to undistort STMap EXR (optional).
            stmap_redistort: Path to redistort STMap EXR (optional).

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
            jsx_lines.append("comp.displayStartFrame = {};".format(
                int(start_frame)))
            jsx_lines.append("")

            # Camera
            if camera:
                cam_jsx = self._jsx_camera(
                    camera, start_frame, end_frame, fps,
                    comp_width, comp_height, ae_scale
                )
                jsx_lines.extend(cam_jsx)
                # Camera scrub leaves Maya at end_frame — reset to
                # start_frame so static geo is sampled correctly.
                cmds.currentTime(int(start_frame), edit=True)

            # Export OBJs and generate null layers
            if geo_children:
                for child in geo_children:
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

            # Mesh Warp lens distortion presets (adjustment layers at top)
            if stmap_undistort or stmap_redistort:
                ae_dir = os.path.dirname(os.path.abspath(jsx_path))
                mw_folder = os.path.basename(os.path.dirname(ae_dir))
                _, v_str = VersionParser.parse_folder_name(mw_folder)
                mw_jsx = self._export_mesh_warp_presets(
                    ae_dir, scene_base, v_str,
                    stmap_undistort, stmap_redistort,
                    fps, start_frame, duration)
                jsx_lines.extend(mw_jsx)

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
# PySide2/6 Stylesheet
# ---------------------------------------------------------------------------
STYLESHEET = """
QWidget {
    background-color: #3a3a3a;
    color: #e0e0e0;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
}
QGroupBox {
    border: 1px solid #555;
    border-radius: 4px;
    margin-top: 10px;
    padding: 18px 6px 8px 6px;
    font-weight: bold;
    font-size: 13px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
}
QGroupBox::indicator {
    width: 12px;
    height: 12px;
}
QTabWidget::pane {
    border: 1px solid #555;
    background-color: #3a3a3a;
}
QTabBar::tab {
    background-color: #444;
    color: #ccc;
    padding: 7px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 3px;
}
QTabBar::tab:selected {
    background-color: #3a3a3a;
    color: #e0e0e0;
    border-bottom: 2px solid #5dade2;
}
QLineEdit, QSpinBox, QComboBox {
    background-color: #2a2a2a;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 4px 8px;
    color: #e0e0e0;
}
QPushButton {
    background-color: #4a4a4a;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 5px 14px;
    color: #e0e0e0;
}
QPushButton:hover {
    background-color: #555;
}
QPushButton:pressed {
    background-color: #333;
}
QPushButton#exportButton {
    background-color: #339956;
    color: white;
    font-size: 14px;
    font-weight: bold;
    border: none;
    border-radius: 4px;
    padding: 8px;
}
QPushButton#exportButton:hover {
    background-color: #3dae64;
}
QPushButton#exportButton:pressed {
    background-color: #2d8049;
}
QProgressBar {
    background-color: #2a2a2a;
    border: 1px solid #555;
    border-radius: 3px;
    text-align: center;
    color: #e0e0e0;
}
QProgressBar::chunk {
    background-color: #5dade2;
    border-radius: 2px;
}
QTextEdit#logField {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Consolas", "Monaco", "Courier New", monospace;
    font-size: 11px;
    border: 1px solid #555;
    border-radius: 3px;
}
QCheckBox {
    spacing: 8px;
    padding: 2px 0;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
}
QSlider::groove:horizontal {
    height: 4px;
    background-color: #555;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background-color: #5dade2;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QLabel {
    font-size: 13px;
}
QScrollArea {
    border: none;
}
"""


# ---------------------------------------------------------------------------
# CollapsibleGroupBox
# ---------------------------------------------------------------------------
class CollapsibleGroupBox(QGroupBox):
    """QGroupBox that collapses/expands its content when the title is clicked."""

    def __init__(self, title="", parent=None):
        super(CollapsibleGroupBox, self).__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(True)
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked):
        for child in self.findChildren(QWidget):
            if child.parent() == self or child.parent().parent() == self:
                child.setVisible(checked)


# ---------------------------------------------------------------------------
# ExportGenieWidget (PySide2/6 UI)
# ---------------------------------------------------------------------------
class ExportGenieWidget(MayaQWidgetDockableMixin, QWidget):
    """Main Export Genie UI — PySide2/6 dockable widget."""

    def __init__(self, parent=None):
        super(ExportGenieWidget, self).__init__(parent)
        self.setObjectName("exportGenie")
        self.setWindowTitle("Export Genie  {}".format(TOOL_VERSION))
        self.setMinimumWidth(380)
        # Shared
        self.scene_info_label = None
        self.export_root_field = None
        self.export_name_field = None
        self.start_frame_spin = None
        self.end_frame_spin = None
        self.tpose_checkbox = None
        self.tpose_frame_spin = None
        self.log_field = None
        self.progress_bar = None
        self.progress_label = None
        self.tab_widget = None
        # Camera Track tab (ct_)
        self.ct_camera_entries = []
        self.ct_camera_layout = None
        self.ct_cam_minus_btn = None
        self.ct_geo_fields = []
        self.ct_geo_layout = None
        self.ct_minus_btn = None
        self.ct_obj_track_entries = []
        self.ct_obj_track_layout = None
        self.ct_obj_track_minus_btn = None
        self.ct_stmap_undistort_field = None
        self.ct_stmap_redistort_field = None
        self.ct_ma_checkbox = None
        self.ct_jsx_checkbox = None
        self.ct_fbx_checkbox = None
        self.ct_abc_checkbox = None
        self.ct_usd_checkbox = None
        self.ct_mov_checkbox = None
        # Playblast settings
        self.pb_context_menu = None
        self.pb_raw_playblast_cb = None
        self.pb_custom_vt_cb = None
        self.pb_wireframe_shader_cb = None
        self.pb_aa16_cb = None
        self.pb_motion_blur_cb = None
        self.pb_hud_overlay_cb = None
        self.pb_far_clip_spin = None
        self.pb_checker_color_btn = None
        self.pb_checker_scale_spin = None
        self.pb_checker_opacity_spin = None
        # Matchmove tab (mm_)
        self.mm_camera_entries = []
        self.mm_camera_layout = None
        self.mm_cam_plus_btn = None
        self.mm_cam_minus_btn = None
        self.mm_static_geo_fields = []
        self.mm_static_geo_layout = None
        self.mm_static_minus_btn = None
        self.mm_rig_geo_pairs = []
        self.mm_rig_geo_layout = None
        self.mm_minus_btn = None
        self.mm_ma_checkbox = None
        self.mm_fbx_checkbox = None
        self.mm_abc_checkbox = None
        self.mm_usd_checkbox = None
        self.mm_mov_checkbox = None
        # Face Track tab (ft_)
        self.ft_camera_entries = []
        self.ft_camera_layout = None
        self.ft_cam_plus_btn = None
        self.ft_cam_minus_btn = None
        self.ft_static_geo_entries = []
        self.ft_static_geo_layout = None
        self.ft_sg_plus_btn = None
        self.ft_sg_minus_btn = None
        self.ft_face_mesh_entries = []
        self.ft_face_mesh_layout = None
        self.ft_minus_btn = None
        self.ft_ma_checkbox = None
        self.ft_fbx_checkbox = None
        self.ft_usd_checkbox = None
        self.ft_mov_checkbox = None
        # Preview mode state
        self._preview_active = False
        self._preview_state = {}
        self._preview_buttons = []
        self._preview_hints = []
        # Progress tracking
        self._progress_total = 1
        self._progress_done = 0
        self._last_export_tab = TAB_CAMERA_TRACK
        # Scene jobs
        self._scene_jobs = []

        # Build the UI
        self._build_ui()
        self.setStyleSheet(STYLESHEET)
        self._refresh_scene_info()

    # ------------------------------------------------------------------
    # Scene Jobs
    # ------------------------------------------------------------------

    def _register_scene_jobs(self):
        """Register Maya scriptJobs for scene events."""
        for event in ("SceneOpened", "SceneSaved", "NewSceneOpened"):
            job_id = cmds.scriptJob(
                event=[event, self._refresh_scene_info],
            )
            self._scene_jobs.append(job_id)

    def closeEvent(self, event):
        """Clean up preview mode and scriptJobs on close."""
        if self._preview_active:
            self._exit_preview_mode()
        for job_id in self._scene_jobs:
            try:
                if cmds.scriptJob(exists=job_id):
                    cmds.scriptJob(kill=job_id)
            except Exception:
                pass
        self._scene_jobs = []
        super(ExportGenieWidget, self).closeEvent(event)

    # ------------------------------------------------------------------
    # UI Builders
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Build the complete widget tree."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(8, 8, 8, 8)
        self._content_layout.setSpacing(6)

        self._build_support_row()
        self._build_scene_info()
        self._build_export_root()

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._build_camera_track_tab(), "Camera Track")
        self.tab_widget.addTab(self._build_matchmove_tab(), "Matchmove")
        self.tab_widget.addTab(self._build_face_track_tab(), "Face Track")
        self.tab_widget.addTab(self._build_playblast_tab(), "Playblast Settings")
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self._content_layout.addWidget(self.tab_widget)

        self._build_frame_range()
        self._build_export_button()
        self._build_progress()
        self._build_log()

        # Version label
        ver_label = QLabel(TOOL_VERSION)
        ver_label.setAlignment(Qt.AlignRight)
        ver_label.setStyleSheet("font-style: italic; font-size: 10px;")
        self._content_layout.addWidget(ver_label)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _build_support_row(self):
        row = QHBoxLayout()
        ver_label = QLabel("{} {}".format(TOOL_NAME, TOOL_VERSION))
        ver_label.setStyleSheet(
            "color: #888888; font-size: 15px; font-weight: bold;")
        row.addWidget(ver_label)
        row.addStretch()
        row.addWidget(QLabel("For Support - "))
        link = QPushButton("Shannon")
        link.setStyleSheet(
            "font-weight: bold; border: none; color: #5dade2; padding: 0;")
        link.setCursor(Qt.PointingHandCursor)
        link.setFlat(True)
        link.clicked.connect(lambda: __import__("webbrowser").open(
            "mailto:sgold1@pdoexperts.fb.com"
            "?subject=Export Genie {}".format(TOOL_VERSION)))
        link.setToolTip("sgold1@pdoexperts.fb.com")
        row.addWidget(link)
        self._content_layout.addLayout(row)

    def _build_scene_info(self):
        group = CollapsibleGroupBox("Scene Info")
        layout = QVBoxLayout()
        layout.setSpacing(4)
        self.scene_info_label = QLabel("Scene: (none)")
        layout.addWidget(self.scene_info_label)
        group.setLayout(layout)
        self._content_layout.addWidget(group)

    def _build_export_root(self):
        group = CollapsibleGroupBox("Export Directory")
        layout = QVBoxLayout()
        layout.setSpacing(6)

        path_row = QHBoxLayout()
        path_row.setSpacing(6)
        lbl = QLabel("Path:")
        lbl.setFixedWidth(40)
        path_row.addWidget(lbl)
        self.export_root_field = QLineEdit()
        self.export_root_field.setToolTip(
            "Root directory for all exported files")
        path_row.addWidget(self.export_root_field, 2)
        browse_btn = QPushButton("Browse...")
        browse_btn.setFixedWidth(85)
        browse_btn.clicked.connect(self._browse_export_root)
        path_row.addWidget(browse_btn)
        layout.addLayout(path_row)

        name_row = QHBoxLayout()
        name_row.setSpacing(6)
        nlbl = QLabel("Export Folder:")
        nlbl.setFixedWidth(80)
        name_row.addWidget(nlbl)
        self.export_name_field = QLineEdit()
        self.export_name_field.setToolTip(
            "Export folder name. Auto-populated from the scene "
            "filename — edit to customize. The version and tag "
            "segments are used for file naming.")
        name_row.addWidget(self.export_name_field, 2)
        layout.addLayout(name_row)

        group.setLayout(layout)
        self._content_layout.addWidget(group)

    def _build_camera_track_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(6)

        # Node Picker
        picker = CollapsibleGroupBox("Node Picker  (In the outliner)")
        picker_layout = QVBoxLayout()
        picker_layout.setSpacing(6)

        # Dynamic camera fields
        self.ct_camera_layout = QVBoxLayout()
        self.ct_camera_layout.setSpacing(6)
        picker_layout.addLayout(self.ct_camera_layout)

        # +/- buttons created here, injected into first row below
        self.ct_cam_plus_btn = QPushButton("+")
        self.ct_cam_plus_btn.setFixedWidth(26)
        self.ct_cam_plus_btn.setToolTip("Add another camera")
        self.ct_cam_plus_btn.clicked.connect(self._add_ct_camera_field)
        self.ct_cam_minus_btn = QPushButton("-")
        self.ct_cam_minus_btn.setFixedWidth(26)
        self.ct_cam_minus_btn.setVisible(False)
        self.ct_cam_minus_btn.setToolTip("Remove the last camera")
        self.ct_cam_minus_btn.clicked.connect(self._remove_ct_camera_field)

        # Separator between cameras and geo
        cam_geo_sep = QFrame()
        cam_geo_sep.setFrameShape(QFrame.HLine)
        cam_geo_sep.setStyleSheet("color: #555;")
        picker_layout.addWidget(cam_geo_sep)

        # Dynamic geo fields container
        self.ct_geo_layout = QVBoxLayout()
        self.ct_geo_layout.setSpacing(6)
        picker_layout.addLayout(self.ct_geo_layout)

        self.ct_geo_plus_btn = QPushButton("+")
        self.ct_geo_plus_btn.setFixedWidth(26)
        self.ct_geo_plus_btn.setToolTip("Add another geo group")
        self.ct_geo_plus_btn.clicked.connect(self._add_ct_geo_field)
        self.ct_minus_btn = QPushButton("-")
        self.ct_minus_btn.setFixedWidth(26)
        self.ct_minus_btn.setVisible(False)
        self.ct_minus_btn.setToolTip("Remove the last geo group")
        self.ct_minus_btn.clicked.connect(self._remove_ct_geo_field)

        # Separator between geo and object tracks
        geo_obj_sep = QFrame()
        geo_obj_sep.setFrameShape(QFrame.HLine)
        geo_obj_sep.setStyleSheet("color: #555;")
        picker_layout.addWidget(geo_obj_sep)

        # Dynamic object track fields
        self.ct_obj_track_layout = QVBoxLayout()
        self.ct_obj_track_layout.setSpacing(6)
        picker_layout.addLayout(self.ct_obj_track_layout)

        self.ct_obj_track_plus_btn = QPushButton("+")
        self.ct_obj_track_plus_btn.setFixedWidth(26)
        self.ct_obj_track_plus_btn.setToolTip("Add another object track")
        self.ct_obj_track_plus_btn.clicked.connect(
            self._add_ct_obj_track_field)
        self.ct_obj_track_minus_btn = QPushButton("-")
        self.ct_obj_track_minus_btn.setFixedWidth(26)
        self.ct_obj_track_minus_btn.setVisible(False)
        self.ct_obj_track_minus_btn.setToolTip(
            "Remove the last object track")
        self.ct_obj_track_minus_btn.clicked.connect(
            self._remove_ct_obj_track_field)

        picker.setLayout(picker_layout)
        tab_layout.addWidget(picker)

        # Add first camera, geo, and object track fields
        # then inject +/- buttons into each first row
        self._add_ct_camera_field()
        fr = self.ct_camera_entries[0]["widget"].layout().itemAt(1).layout()
        idx = fr.count() - 1
        fr.insertSpacing(idx, 12)
        fr.insertWidget(idx + 1, self.ct_cam_plus_btn)
        fr.insertWidget(idx + 2, self.ct_cam_minus_btn)

        self._add_ct_geo_field()
        fr = self.ct_geo_fields[0]["widget"].layout().itemAt(1).layout()
        idx = fr.count() - 1
        fr.insertSpacing(idx, 12)
        fr.insertWidget(idx + 1, self.ct_geo_plus_btn)
        fr.insertWidget(idx + 2, self.ct_minus_btn)

        self._add_ct_obj_track_field()
        fr = self.ct_obj_track_entries[0]["widget"].layout().itemAt(1).layout()
        idx = fr.count() - 1
        fr.insertSpacing(idx, 12)
        fr.insertWidget(idx + 1, self.ct_obj_track_plus_btn)
        fr.insertWidget(idx + 2, self.ct_obj_track_minus_btn)

        # Lens Distortion STMaps (for AE Grid Warp)
        stmap_group = CollapsibleGroupBox(
            "Lens Distortion STMaps  (for AE Grid Warp)")
        stmap_layout = QVBoxLayout()
        stmap_layout.setSpacing(6)

        ud_lbl = QLabel("Undistort STMap (.exr):")
        stmap_layout.addWidget(ud_lbl)
        ud_row = QHBoxLayout()
        ud_row.setSpacing(6)
        self.ct_stmap_undistort_field = QLineEdit()
        self.ct_stmap_undistort_field.setReadOnly(True)
        self.ct_stmap_undistort_field.setToolTip(
            "32-bit EXR STMap for removing lens distortion")
        ud_row.addWidget(self.ct_stmap_undistort_field, 2)
        ud_btn = QPushButton("Browse...")
        ud_btn.setFixedWidth(85)
        ud_btn.clicked.connect(
            partial(self._browse_stmap, self.ct_stmap_undistort_field))
        ud_row.addWidget(ud_btn)
        stmap_layout.addLayout(ud_row)

        rd_lbl = QLabel("Redistort STMap (.exr):")
        stmap_layout.addWidget(rd_lbl)
        rd_row = QHBoxLayout()
        rd_row.setSpacing(6)
        self.ct_stmap_redistort_field = QLineEdit()
        self.ct_stmap_redistort_field.setReadOnly(True)
        self.ct_stmap_redistort_field.setToolTip(
            "32-bit EXR STMap for re-applying lens distortion")
        rd_row.addWidget(self.ct_stmap_redistort_field, 2)
        rd_btn = QPushButton("Browse...")
        rd_btn.setFixedWidth(85)
        rd_btn.clicked.connect(
            partial(self._browse_stmap, self.ct_stmap_redistort_field))
        rd_row.addWidget(rd_btn)
        stmap_layout.addLayout(rd_row)

        stmap_group.setLayout(stmap_layout)
        tab_layout.addWidget(stmap_group)

        # Export Formats
        formats = CollapsibleGroupBox("Export Formats")
        fmt_layout = QVBoxLayout()
        fmt_layout.setSpacing(4)
        self.ct_ma_checkbox = QCheckBox("  Maya ASCII (.ma)")
        self.ct_ma_checkbox.setChecked(True)
        self.ct_jsx_checkbox = QCheckBox("  After Effects (.jsx + .obj)")
        self.ct_jsx_checkbox.setChecked(True)
        self.ct_fbx_checkbox = QCheckBox("  FBX (.fbx)")
        self.ct_fbx_checkbox.setChecked(True)
        self.ct_abc_checkbox = QCheckBox("  Alembic (.abc)")
        self.ct_abc_checkbox.setChecked(True)
        self.ct_usd_checkbox = QCheckBox("  USD (.usd)")
        self.ct_usd_checkbox.setChecked(True)

        self.ct_mov_checkbox = QCheckBox("  Playblast QC (.mp4)")
        self.ct_mov_checkbox.setChecked(True)

        fmt_layout.addWidget(self.ct_ma_checkbox)
        fmt_layout.addWidget(self.ct_jsx_checkbox)
        fmt_layout.addWidget(self.ct_fbx_checkbox)
        fmt_layout.addWidget(self.ct_abc_checkbox)
        fmt_layout.addWidget(self.ct_usd_checkbox)
        fmt_layout.addWidget(self.ct_mov_checkbox)
        formats.setLayout(fmt_layout)
        tab_layout.addWidget(formats)

        tab_layout.addStretch()
        return tab

    def _build_matchmove_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(6)

        # Node Picker
        picker = CollapsibleGroupBox("Node Picker  (In the outliner)")
        picker_layout = QVBoxLayout()
        picker_layout.setSpacing(6)

        # Dynamic camera fields
        self.mm_camera_layout = QVBoxLayout()
        self.mm_camera_layout.setSpacing(6)
        picker_layout.addLayout(self.mm_camera_layout)

        self.mm_cam_plus_btn = QPushButton("+")
        self.mm_cam_plus_btn.setFixedWidth(26)
        self.mm_cam_plus_btn.setToolTip("Add another camera")
        self.mm_cam_plus_btn.clicked.connect(self._add_mm_camera_field)
        self.mm_cam_minus_btn = QPushButton("-")
        self.mm_cam_minus_btn.setFixedWidth(26)
        self.mm_cam_minus_btn.setVisible(False)
        self.mm_cam_minus_btn.setToolTip("Remove the last camera")
        self.mm_cam_minus_btn.clicked.connect(self._remove_mm_camera_field)

        # Dynamic static geo fields
        self.mm_static_geo_layout = QVBoxLayout()
        self.mm_static_geo_layout.setSpacing(6)
        picker_layout.addLayout(self.mm_static_geo_layout)

        self.mm_static_plus_btn = QPushButton("+")
        self.mm_static_plus_btn.setFixedWidth(26)
        self.mm_static_plus_btn.setToolTip("Add another static geo group")
        self.mm_static_plus_btn.clicked.connect(self._add_mm_static_geo_field)
        self.mm_static_minus_btn = QPushButton("-")
        self.mm_static_minus_btn.setFixedWidth(26)
        self.mm_static_minus_btn.setVisible(False)
        self.mm_static_minus_btn.setToolTip("Remove the last static geo group")
        self.mm_static_minus_btn.clicked.connect(
            self._remove_mm_static_geo_field)

        # Add first camera, then inject +/- into its row
        self._add_mm_camera_field()
        fr = self.mm_camera_entries[0]["widget"].layout().itemAt(1).layout()
        idx = fr.count() - 1
        fr.insertSpacing(idx, 12)
        fr.insertWidget(idx + 1, self.mm_cam_plus_btn)
        fr.insertWidget(idx + 2, self.mm_cam_minus_btn)

        # Add first static geo field, then inject +/- into its row
        self._add_mm_static_geo_field()
        fr = self.mm_static_geo_fields[0]["widget"].layout().itemAt(1).layout()
        idx = fr.count() - 1
        fr.insertSpacing(idx, 12)
        fr.insertWidget(idx + 1, self.mm_static_plus_btn)
        fr.insertWidget(idx + 2, self.mm_static_minus_btn)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #555;")
        picker_layout.addWidget(sep)

        # Dynamic rig/geo pairs
        self.mm_rig_geo_layout = QVBoxLayout()
        self.mm_rig_geo_layout.setSpacing(6)
        picker_layout.addLayout(self.mm_rig_geo_layout)

        self.mm_rg_plus_btn = QPushButton("+")
        self.mm_rg_plus_btn.setFixedWidth(26)
        self.mm_rg_plus_btn.setToolTip("Add another rig/geo pair")
        self.mm_rg_plus_btn.clicked.connect(self._add_rig_geo_pair)
        self.mm_minus_btn = QPushButton("-")
        self.mm_minus_btn.setFixedWidth(26)
        self.mm_minus_btn.setVisible(False)
        self.mm_minus_btn.setToolTip("Remove the last rig/geo pair")
        self.mm_minus_btn.clicked.connect(self._remove_rig_geo_pair)

        # Add first pair, then inject +/- into its rig row
        self._add_rig_geo_pair()
        first_pair_widget = self.mm_rig_geo_pairs[0]["widget"]
        # VBox: [0]=rig label, [1]=rig field row, [2]=geo label, [3]=geo row
        rig_hlayout = first_pair_widget.layout().itemAt(1).layout()
        idx = rig_hlayout.count() - 1
        rig_hlayout.insertSpacing(idx, 12)
        rig_hlayout.insertWidget(idx + 1, self.mm_rg_plus_btn)
        rig_hlayout.insertWidget(idx + 2, self.mm_minus_btn)

        picker.setLayout(picker_layout)
        tab_layout.addWidget(picker)

        # Export Formats
        formats = CollapsibleGroupBox("Export Formats")
        fmt_layout = QVBoxLayout()
        fmt_layout.setSpacing(4)
        self.mm_ma_checkbox = QCheckBox("  Maya ASCII (.ma)")
        self.mm_ma_checkbox.setChecked(True)
        self.mm_fbx_checkbox = QCheckBox("  FBX (.fbx)")
        self.mm_fbx_checkbox.setChecked(True)
        self.mm_abc_checkbox = QCheckBox("  Alembic (.abc)")
        self.mm_abc_checkbox.setChecked(True)
        self.mm_usd_checkbox = QCheckBox("  USD (.usd)")
        self.mm_usd_checkbox.setChecked(True)

        self.mm_mov_checkbox = QCheckBox("  Playblast QC (.mp4)")
        self.mm_mov_checkbox.setChecked(True)

        fmt_layout.addWidget(self.mm_ma_checkbox)
        fmt_layout.addWidget(self.mm_fbx_checkbox)
        fmt_layout.addWidget(self.mm_abc_checkbox)
        fmt_layout.addWidget(self.mm_usd_checkbox)
        fmt_layout.addWidget(self.mm_mov_checkbox)
        formats.setLayout(fmt_layout)
        tab_layout.addWidget(formats)

        # T-pose
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #555;")
        tab_layout.addWidget(sep2)

        tpose_row = QHBoxLayout()
        tpose_row.setSpacing(8)
        self.tpose_checkbox = QCheckBox("  Include T Pose")
        self.tpose_checkbox.setChecked(True)
        self.tpose_checkbox.setToolTip(
            "Include a T-pose frame before the animation start")
        tpose_row.addWidget(self.tpose_checkbox)
        self.tpose_frame_spin = QSpinBox()
        self.tpose_frame_spin.setRange(-99999, 99999)
        self.tpose_frame_spin.setValue(991)
        self.tpose_frame_spin.setFixedWidth(55)
        self.tpose_frame_spin.setToolTip("Frame number for the T-pose")
        tpose_row.addWidget(self.tpose_frame_spin)
        tpose_row.addStretch()
        tab_layout.addLayout(tpose_row)

        tab_layout.addStretch()
        return tab

    def _build_face_track_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(6)

        # Node Picker
        picker = CollapsibleGroupBox("Node Picker  (In the outliner)")
        picker_layout = QVBoxLayout()
        picker_layout.setSpacing(6)

        # Dynamic camera fields
        self.ft_camera_layout = QVBoxLayout()
        self.ft_camera_layout.setSpacing(6)
        picker_layout.addLayout(self.ft_camera_layout)

        self.ft_cam_plus_btn = QPushButton("+")
        self.ft_cam_plus_btn.setFixedWidth(26)
        self.ft_cam_plus_btn.setToolTip("Add another camera")
        self.ft_cam_plus_btn.clicked.connect(self._add_ft_camera_field)
        self.ft_cam_minus_btn = QPushButton("-")
        self.ft_cam_minus_btn.setFixedWidth(26)
        self.ft_cam_minus_btn.setVisible(False)
        self.ft_cam_minus_btn.setToolTip("Remove the last camera")
        self.ft_cam_minus_btn.clicked.connect(self._remove_ft_camera_field)

        # Dynamic static geo fields
        self.ft_static_geo_layout = QVBoxLayout()
        self.ft_static_geo_layout.setSpacing(6)
        picker_layout.addLayout(self.ft_static_geo_layout)

        self.ft_sg_plus_btn = QPushButton("+")
        self.ft_sg_plus_btn.setFixedWidth(26)
        self.ft_sg_plus_btn.setToolTip("Add another static geo group")
        self.ft_sg_plus_btn.clicked.connect(self._add_ft_static_geo_field)
        self.ft_sg_minus_btn = QPushButton("-")
        self.ft_sg_minus_btn.setFixedWidth(26)
        self.ft_sg_minus_btn.setVisible(False)
        self.ft_sg_minus_btn.setToolTip("Remove the last static geo group")
        self.ft_sg_minus_btn.clicked.connect(
            self._remove_ft_static_geo_field)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #555;")
        picker_layout.addWidget(sep)

        # Dynamic face mesh entries
        self.ft_face_mesh_layout = QVBoxLayout()
        self.ft_face_mesh_layout.setSpacing(6)
        picker_layout.addLayout(self.ft_face_mesh_layout)

        self.ft_plus_btn = QPushButton("+")
        self.ft_plus_btn.setFixedWidth(26)
        self.ft_plus_btn.setToolTip("Add another face mesh entry")
        self.ft_plus_btn.clicked.connect(self._add_face_mesh_entry)
        self.ft_minus_btn = QPushButton("-")
        self.ft_minus_btn.setFixedWidth(26)
        self.ft_minus_btn.setVisible(False)
        self.ft_minus_btn.setToolTip("Remove the last face mesh entry")
        self.ft_minus_btn.clicked.connect(self._remove_face_mesh_entry)

        # Add first camera, static geo, and face mesh entries
        self._add_ft_camera_field()
        fr = self.ft_camera_entries[0]["widget"].layout().itemAt(1).layout()
        idx = fr.count() - 1
        fr.insertSpacing(idx, 12)
        fr.insertWidget(idx + 1, self.ft_cam_plus_btn)
        fr.insertWidget(idx + 2, self.ft_cam_minus_btn)

        self._add_ft_static_geo_field()
        fr = self.ft_static_geo_entries[0]["widget"].layout().itemAt(1).layout()
        idx = fr.count() - 1
        fr.insertSpacing(idx, 12)
        fr.insertWidget(idx + 1, self.ft_sg_plus_btn)
        fr.insertWidget(idx + 2, self.ft_sg_minus_btn)

        self._add_face_mesh_entry()
        fr = self.ft_face_mesh_entries[0]["widget"].layout().itemAt(1).layout()
        idx = fr.count() - 1
        fr.insertSpacing(idx, 12)
        fr.insertWidget(idx + 1, self.ft_plus_btn)
        fr.insertWidget(idx + 2, self.ft_minus_btn)

        picker.setLayout(picker_layout)
        tab_layout.addWidget(picker)

        # Export Formats
        formats = CollapsibleGroupBox("Export Formats")
        fmt_layout = QVBoxLayout()
        fmt_layout.setSpacing(4)
        self.ft_ma_checkbox = QCheckBox("  Maya ASCII (.ma)")
        self.ft_ma_checkbox.setChecked(True)
        self.ft_fbx_checkbox = QCheckBox("  FBX (.fbx)")
        self.ft_fbx_checkbox.setChecked(True)
        self.ft_usd_checkbox = QCheckBox("  USD (.usd)")
        self.ft_usd_checkbox.setChecked(True)

        self.ft_mov_checkbox = QCheckBox("  Playblast QC (.mp4)")
        self.ft_mov_checkbox.setChecked(True)

        fmt_layout.addWidget(self.ft_ma_checkbox)
        fmt_layout.addWidget(self.ft_fbx_checkbox)
        fmt_layout.addWidget(self.ft_usd_checkbox)
        fmt_layout.addWidget(self.ft_mov_checkbox)
        formats.setLayout(fmt_layout)
        tab_layout.addWidget(formats)

        tab_layout.addStretch()
        return tab

    def _build_playblast_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(6)

        # Export Context
        ctx_row = QHBoxLayout()
        ctx_row.setSpacing(8)
        ctx_row.addWidget(QLabel("Export Context:"))
        self.pb_context_menu = QComboBox()
        self.pb_context_menu.addItems(
            ["-- Choose --", "Camera Track", "Matchmove", "Face Track"])
        self.pb_context_menu.setToolTip(
            "Which export tab these settings apply to for preview")
        ctx_row.addWidget(self.pb_context_menu)
        ctx_row.addStretch()
        tab_layout.addLayout(ctx_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #555;")
        tab_layout.addWidget(sep)

        # General
        gen = CollapsibleGroupBox("General")
        gen_layout = QVBoxLayout()
        gen_layout.setSpacing(4)
        self.pb_aa16_cb = QCheckBox("  Anti-Aliasing 16x (increased RAM)")
        self.pb_aa16_cb.setToolTip(
            "Sets VP2.0 MSAA to 16 samples instead of 8.")
        gen_layout.addWidget(self.pb_aa16_cb)

        # Far Clip slider
        fc_row = QHBoxLayout()
        fc_row.setSpacing(8)
        fc_row.addWidget(QLabel("Far Clip:"))
        self.pb_far_clip_spin = QSpinBox()
        self.pb_far_clip_spin.setRange(1000, 10000000)
        self.pb_far_clip_spin.setValue(800000)
        self.pb_far_clip_spin.setFixedWidth(80)
        self.pb_far_clip_spin.setToolTip("Camera far clipping plane")
        fc_slider = QSlider(Qt.Horizontal)
        fc_slider.setRange(10000, 2000000)
        fc_slider.setValue(800000)
        self.pb_far_clip_spin.valueChanged.connect(fc_slider.setValue)
        fc_slider.valueChanged.connect(self.pb_far_clip_spin.setValue)
        fc_row.addWidget(self.pb_far_clip_spin)
        fc_row.addWidget(fc_slider)
        gen_layout.addLayout(fc_row)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #555;")
        gen_layout.addWidget(sep2)

        self.pb_raw_playblast_cb = QCheckBox(
            "  Use Current Viewport Settings")
        self.pb_raw_playblast_cb.setToolTip(
            "Playblast uses your current VP2.0 settings without modifications")
        gen_layout.addWidget(self.pb_raw_playblast_cb)
        self.pb_custom_vt_cb = QCheckBox("  Use Custom View Transform")
        self.pb_custom_vt_cb.setToolTip(
            "When checked, the playblast uses your current view transform "
            "instead of forcing Raw (sRGB)")
        gen_layout.addWidget(self.pb_custom_vt_cb)
        self.pb_hud_overlay_cb = QCheckBox(
            "  Show Frame / Focal Length HUD")
        self.pb_hud_overlay_cb.setChecked(True)
        self.pb_hud_overlay_cb.setToolTip(
            "Burn frame number and focal length into the playblast")
        gen_layout.addWidget(self.pb_hud_overlay_cb)
        gen.setLayout(gen_layout)
        tab_layout.addWidget(gen)

        # Camera Track
        ct = CollapsibleGroupBox("Camera Track")
        ct_layout = QVBoxLayout()
        ct_layout.setSpacing(4)
        self.pb_wireframe_shader_cb = QCheckBox(
            "  useBackground Shader + Wireframe")
        self.pb_wireframe_shader_cb.setChecked(True)
        self.pb_wireframe_shader_cb.setToolTip(
            "Applies a useBackground shader to all geo with "
            "wireframe-on-shaded for the playblast")
        ct_layout.addWidget(self.pb_wireframe_shader_cb)
        ct.setLayout(ct_layout)
        tab_layout.addWidget(ct)

        # Matchmove / Face Track
        mmft = CollapsibleGroupBox("Matchmove / Face Track")
        mmft_layout = QVBoxLayout()
        mmft_layout.setSpacing(4)
        self.pb_motion_blur_cb = QCheckBox("  Motion Blur")
        self.pb_motion_blur_cb.setChecked(True)
        self.pb_motion_blur_cb.setToolTip(
            "Enable VP2.0 motion blur during playblast")
        mmft_layout.addWidget(self.pb_motion_blur_cb)
        mmft_layout.addWidget(QLabel("QC Checker Overlay"))

        # Color
        clr_row = QHBoxLayout()
        clr_row.setSpacing(8)
        clr_row.addWidget(QLabel("Color:"))
        self.pb_checker_color_btn = QPushButton()
        self.pb_checker_color_btn._color = (0.6, 0.1, 0.1)
        self._update_color_button(self.pb_checker_color_btn)
        self.pb_checker_color_btn.setFixedWidth(100)
        self.pb_checker_color_btn.setToolTip("Color of the UV checker overlay")
        self.pb_checker_color_btn.clicked.connect(
            lambda: self._pick_color(self.pb_checker_color_btn))
        clr_row.addWidget(self.pb_checker_color_btn)
        clr_row.addStretch()
        mmft_layout.addLayout(clr_row)

        # Scale slider
        sc_row = QHBoxLayout()
        sc_row.setSpacing(8)
        sc_row.addWidget(QLabel("Scale:"))
        self.pb_checker_scale_spin = QSpinBox()
        self.pb_checker_scale_spin.setRange(1, 32)
        self.pb_checker_scale_spin.setValue(15)
        self.pb_checker_scale_spin.setFixedWidth(50)
        self.pb_checker_scale_spin.setToolTip("Scale of the UV checker pattern")
        sc_slider = QSlider(Qt.Horizontal)
        sc_slider.setRange(1, 32)
        sc_slider.setValue(15)
        self.pb_checker_scale_spin.valueChanged.connect(sc_slider.setValue)
        sc_slider.valueChanged.connect(self.pb_checker_scale_spin.setValue)
        sc_row.addWidget(self.pb_checker_scale_spin)
        sc_row.addWidget(sc_slider)
        mmft_layout.addLayout(sc_row)

        # Opacity slider
        op_row = QHBoxLayout()
        op_row.setSpacing(8)
        op_row.addWidget(QLabel("Blend:"))
        self.pb_checker_opacity_spin = QSpinBox()
        self.pb_checker_opacity_spin.setRange(0, 100)
        self.pb_checker_opacity_spin.setValue(30)
        self.pb_checker_opacity_spin.setFixedWidth(50)
        self.pb_checker_opacity_spin.setToolTip(
            "Overlay blend opacity (0=plate only, 100=full mesh overlay)")
        op_slider = QSlider(Qt.Horizontal)
        op_slider.setRange(0, 100)
        op_slider.setValue(30)
        self.pb_checker_opacity_spin.valueChanged.connect(op_slider.setValue)
        op_slider.valueChanged.connect(self.pb_checker_opacity_spin.setValue)
        op_row.addWidget(self.pb_checker_opacity_spin)
        op_row.addWidget(op_slider)
        mmft_layout.addLayout(op_row)

        mmft.setLayout(mmft_layout)
        tab_layout.addWidget(mmft)

        # Preview
        sep3 = QFrame()
        sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet("color: #555;")
        tab_layout.addWidget(sep3)
        pb_preview_hint = QLabel(
            "Re-toggle preview to apply setting changes.")
        pb_preview_hint.setVisible(False)
        pb_preview_hint.setStyleSheet("font-style: italic; font-size: 10px;")
        self._preview_hints.append(pb_preview_hint)
        tab_layout.addWidget(pb_preview_hint)
        pb_preview_btn = QPushButton("Preview Playblast")
        pb_preview_btn.setFixedHeight(28)
        pb_preview_btn.setToolTip(
            "Toggle live viewport preview of playblast settings.")
        pb_preview_btn.clicked.connect(self._on_preview_playblast)
        self._preview_buttons.append(pb_preview_btn)
        tab_layout.addWidget(pb_preview_btn)

        tab_layout.addStretch()
        return tab

    def _build_frame_range(self):
        group = CollapsibleGroupBox("Frame Range")
        layout = QVBoxLayout()
        layout.setSpacing(6)

        fr_row = QHBoxLayout()
        fr_row.setSpacing(6)
        fr_row.addWidget(QLabel("Start:"))
        spin_pad_ss = "QSpinBox::up-button, QSpinBox::down-button { left: 3px; }"
        self.start_frame_spin = QSpinBox()
        self.start_frame_spin.setRange(-999999, 999999)
        self.start_frame_spin.setValue(1001)
        self.start_frame_spin.setFixedWidth(68)
        self.start_frame_spin.setStyleSheet(spin_pad_ss)
        self.start_frame_spin.setToolTip("First frame of the export range")
        fr_row.addWidget(self.start_frame_spin)
        fr_row.addSpacing(24)
        fr_row.addWidget(QLabel("End:"))
        self.end_frame_spin = QSpinBox()
        self.end_frame_spin.setRange(-999999, 999999)
        self.end_frame_spin.setValue(1001)
        self.end_frame_spin.setFixedWidth(68)
        self.end_frame_spin.setStyleSheet(spin_pad_ss)
        self.end_frame_spin.setToolTip("Last frame of the export range")
        fr_row.addWidget(self.end_frame_spin)
        fr_row.addStretch()
        layout.addLayout(fr_row)

        tl_btn = QPushButton("Use Timeline Range")
        tl_btn.setToolTip("Set start/end frames from the scene timeline")
        tl_btn.clicked.connect(self._set_timeline_range)
        layout.addWidget(tl_btn)

        group.setLayout(layout)
        self._content_layout.addWidget(group)

    def _build_export_button(self):
        self._content_layout.addSpacing(8)
        export_btn = QPushButton("E X P O R T")
        export_btn.setObjectName("exportButton")
        export_btn.setFixedHeight(40)
        export_btn.setToolTip("Run the export for all checked formats")
        export_btn.clicked.connect(self._on_export)
        self._content_layout.addWidget(export_btn)
        self._content_layout.addSpacing(4)

    def _build_progress(self):
        prog_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setVisible(False)
        prog_row.addWidget(self.progress_bar)
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignRight)
        self.progress_label.setStyleSheet("font-size: 10px;")
        self.progress_label.setVisible(False)
        prog_row.addWidget(self.progress_label)
        self._content_layout.addLayout(prog_row)

    def _build_log(self):
        group = CollapsibleGroupBox("Status")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 2, 0, 0)
        self.log_field = QTextEdit()
        self.log_field.setObjectName("logField")
        self.log_field.setReadOnly(True)
        self.log_field.setFixedHeight(480)
        layout.addWidget(self.log_field)
        group.setLayout(layout)
        self._content_layout.addWidget(group)

    # ------------------------------------------------------------------
    # Dynamic Field Lists
    # ------------------------------------------------------------------

    def _add_ct_camera_field(self):
        idx = len(self.ct_camera_entries) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(2)
        lbl = QLabel("Camera{}:".format(suffix))
        row_layout.addWidget(lbl)
        field_row = QHBoxLayout()
        field_row.setSpacing(6)
        field = QLineEdit()
        field.setReadOnly(True)
        field.setToolTip("Select a camera to export")
        field_row.addWidget(field, 2)
        btn = QPushButton("<< Load Sel")
        btn.setFixedWidth(100)
        btn.clicked.connect(
            partial(self._load_selection_into, field, "camera"))
        field_row.addWidget(btn)
        row_layout.addLayout(field_row)

        self.ct_camera_layout.addWidget(row)
        self.ct_camera_entries.append({"widget": row, "field": field})
        if self.ct_cam_minus_btn:
            self.ct_cam_minus_btn.setVisible(
                len(self.ct_camera_entries) >= 2)

    def _remove_ct_camera_field(self):
        if len(self.ct_camera_entries) <= 1:
            return
        entry = self.ct_camera_entries.pop()
        entry["widget"].deleteLater()
        self.ct_cam_minus_btn.setVisible(
            len(self.ct_camera_entries) >= 2)

    def _add_ct_geo_field(self):
        idx = len(self.ct_geo_fields) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(2)
        lbl = QLabel("Geo Group{}:".format(suffix))
        row_layout.addWidget(lbl)
        field_row = QHBoxLayout()
        field_row.setSpacing(6)
        field = QLineEdit()
        field.setReadOnly(True)
        field.setToolTip("Select a top-level geo group to export")
        field_row.addWidget(field, 2)
        btn = QPushButton("<< Load Sel")
        btn.setFixedWidth(100)
        btn.clicked.connect(
            partial(self._load_selection_into, field, "geo"))
        field_row.addWidget(btn)
        row_layout.addLayout(field_row)

        self.ct_geo_layout.addWidget(row)
        self.ct_geo_fields.append({"widget": row, "field": field})
        if self.ct_minus_btn:
            self.ct_minus_btn.setVisible(len(self.ct_geo_fields) >= 2)

    def _remove_ct_geo_field(self):
        if len(self.ct_geo_fields) <= 1:
            return
        entry = self.ct_geo_fields.pop()
        entry["widget"].deleteLater()
        self.ct_minus_btn.setVisible(len(self.ct_geo_fields) >= 2)

    def _add_ct_obj_track_field(self):
        idx = len(self.ct_obj_track_entries) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(2)
        lbl = QLabel("Object Track{}:".format(suffix))
        row_layout.addWidget(lbl)
        field_row = QHBoxLayout()
        field_row.setSpacing(6)
        field = QLineEdit()
        field.setReadOnly(True)
        field.setToolTip("Select an object track to export")
        field_row.addWidget(field, 2)
        btn = QPushButton("<< Load Sel")
        btn.setFixedWidth(100)
        btn.clicked.connect(
            partial(self._load_selection_into, field, "geo"))
        field_row.addWidget(btn)
        row_layout.addLayout(field_row)

        self.ct_obj_track_layout.addWidget(row)
        self.ct_obj_track_entries.append({"widget": row, "field": field})
        if self.ct_obj_track_minus_btn:
            self.ct_obj_track_minus_btn.setVisible(
                len(self.ct_obj_track_entries) >= 2)

    def _remove_ct_obj_track_field(self):
        if len(self.ct_obj_track_entries) <= 1:
            return
        entry = self.ct_obj_track_entries.pop()
        entry["widget"].deleteLater()
        self.ct_obj_track_minus_btn.setVisible(
            len(self.ct_obj_track_entries) >= 2)

    def _add_mm_camera_field(self):
        idx = len(self.mm_camera_entries) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(2)
        lbl = QLabel("Camera{}:".format(suffix))
        row_layout.addWidget(lbl)
        field_row = QHBoxLayout()
        field_row.setSpacing(6)
        field = QLineEdit()
        field.setReadOnly(True)
        field.setToolTip("Select a camera to export")
        field_row.addWidget(field, 2)
        btn = QPushButton("<< Load Sel")
        btn.setFixedWidth(100)
        btn.clicked.connect(
            partial(self._load_selection_into, field, "camera"))
        field_row.addWidget(btn)
        row_layout.addLayout(field_row)

        self.mm_camera_layout.addWidget(row)
        self.mm_camera_entries.append({"widget": row, "field": field})
        if self.mm_cam_minus_btn:
            self.mm_cam_minus_btn.setVisible(
                len(self.mm_camera_entries) >= 2)

    def _remove_mm_camera_field(self):
        if len(self.mm_camera_entries) <= 1:
            return
        entry = self.mm_camera_entries.pop()
        entry["widget"].deleteLater()
        self.mm_cam_minus_btn.setVisible(
            len(self.mm_camera_entries) >= 2)

    def _add_mm_static_geo_field(self):
        idx = len(self.mm_static_geo_fields) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(2)
        lbl = QLabel("Static Geo{}:".format(suffix))
        row_layout.addWidget(lbl)
        field_row = QHBoxLayout()
        field_row.setSpacing(6)
        field = QLineEdit()
        field.setReadOnly(True)
        field.setToolTip("Select static/proxy geometry group")
        field_row.addWidget(field, 2)
        btn = QPushButton("<< Load Sel")
        btn.setFixedWidth(100)
        btn.clicked.connect(
            partial(self._load_selection_into, field, "proxy"))
        field_row.addWidget(btn)
        row_layout.addLayout(field_row)

        self.mm_static_geo_layout.addWidget(row)
        self.mm_static_geo_fields.append({"widget": row, "field": field})
        if self.mm_static_minus_btn:
            self.mm_static_minus_btn.setVisible(
                len(self.mm_static_geo_fields) >= 2)

    def _remove_mm_static_geo_field(self):
        if len(self.mm_static_geo_fields) <= 1:
            return
        entry = self.mm_static_geo_fields.pop()
        entry["widget"].deleteLater()
        self.mm_static_minus_btn.setVisible(
            len(self.mm_static_geo_fields) >= 2)

    def _add_rig_geo_pair(self):
        idx = len(self.mm_rig_geo_pairs) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(2)

        rlbl = QLabel("Main Rig Group{}:".format(suffix))
        row_layout.addWidget(rlbl)
        rig_row = QHBoxLayout()
        rig_row.setSpacing(6)
        rig_field = QLineEdit()
        rig_field.setReadOnly(True)
        rig_field.setToolTip("Select the control rig group")
        rig_row.addWidget(rig_field, 2)
        rig_btn = QPushButton("<< Load Sel")
        rig_btn.setFixedWidth(100)
        rig_btn.clicked.connect(
            partial(self._load_selection_into, rig_field, "rig"))
        rig_row.addWidget(rig_btn)
        row_layout.addLayout(rig_row)

        glbl = QLabel("Mesh Group{}:".format(suffix))
        row_layout.addWidget(glbl)
        geo_row = QHBoxLayout()
        geo_row.setSpacing(6)
        geo_field = QLineEdit()
        geo_field.setReadOnly(True)
        geo_field.setToolTip("Select the animated geo group")
        geo_row.addWidget(geo_field, 2)
        geo_btn = QPushButton("<< Load Sel")
        geo_btn.setFixedWidth(100)
        geo_btn.clicked.connect(
            partial(self._load_selection_into, geo_field, "geo"))
        geo_row.addWidget(geo_btn)
        row_layout.addLayout(geo_row)

        self.mm_rig_geo_layout.addWidget(row)
        self.mm_rig_geo_pairs.append({
            "rig_field": rig_field,
            "geo_field": geo_field,
            "widget": row,
        })
        if self.mm_minus_btn:
            self.mm_minus_btn.setVisible(len(self.mm_rig_geo_pairs) >= 2)

    def _remove_rig_geo_pair(self):
        if len(self.mm_rig_geo_pairs) <= 1:
            return
        entry = self.mm_rig_geo_pairs.pop()
        entry["widget"].deleteLater()
        self.mm_minus_btn.setVisible(len(self.mm_rig_geo_pairs) >= 2)

    def _add_ft_camera_field(self):
        idx = len(self.ft_camera_entries) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(2)
        lbl = QLabel("Camera{}:".format(suffix))
        row_layout.addWidget(lbl)
        field_row = QHBoxLayout()
        field_row.setSpacing(6)
        field = QLineEdit()
        field.setReadOnly(True)
        field.setToolTip("Select a camera to export")
        field_row.addWidget(field, 2)
        btn = QPushButton("<< Load Sel")
        btn.setFixedWidth(100)
        btn.clicked.connect(
            partial(self._load_selection_into, field, "camera"))
        field_row.addWidget(btn)
        row_layout.addLayout(field_row)

        self.ft_camera_layout.addWidget(row)
        self.ft_camera_entries.append({"widget": row, "field": field})
        if self.ft_cam_minus_btn:
            self.ft_cam_minus_btn.setVisible(
                len(self.ft_camera_entries) >= 2)

    def _remove_ft_camera_field(self):
        if len(self.ft_camera_entries) <= 1:
            return
        entry = self.ft_camera_entries.pop()
        entry["widget"].deleteLater()
        self.ft_cam_minus_btn.setVisible(
            len(self.ft_camera_entries) >= 2)

    def _add_ft_static_geo_field(self):
        idx = len(self.ft_static_geo_entries) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(2)
        lbl = QLabel("Static Geo{}:".format(suffix))
        row_layout.addWidget(lbl)
        field_row = QHBoxLayout()
        field_row.setSpacing(6)
        field = QLineEdit()
        field.setReadOnly(True)
        field.setToolTip("Select static geometry group")
        field_row.addWidget(field, 2)
        btn = QPushButton("<< Load Sel")
        btn.setFixedWidth(100)
        btn.clicked.connect(
            partial(self._load_selection_into, field, "proxy"))
        field_row.addWidget(btn)
        row_layout.addLayout(field_row)

        self.ft_static_geo_layout.addWidget(row)
        self.ft_static_geo_entries.append(
            {"widget": row, "field": field})
        if self.ft_sg_minus_btn:
            self.ft_sg_minus_btn.setVisible(
                len(self.ft_static_geo_entries) >= 2)

    def _remove_ft_static_geo_field(self):
        if len(self.ft_static_geo_entries) <= 1:
            return
        entry = self.ft_static_geo_entries.pop()
        entry["widget"].deleteLater()
        self.ft_sg_minus_btn.setVisible(
            len(self.ft_static_geo_entries) >= 2)

    def _add_face_mesh_entry(self):
        idx = len(self.ft_face_mesh_entries) + 1
        suffix = "" if idx == 1 else " {}".format(idx)

        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(2)
        lbl = QLabel("Face Mesh{}:".format(suffix))
        row_layout.addWidget(lbl)
        field_row = QHBoxLayout()
        field_row.setSpacing(6)
        field = QLineEdit()
        field.setReadOnly(True)
        field.setToolTip("Select a face mesh to export")
        field_row.addWidget(field, 2)
        btn = QPushButton("<< Load Sel")
        btn.setFixedWidth(100)
        btn.clicked.connect(
            partial(self._load_selection_into, field, "geo"))
        field_row.addWidget(btn)
        row_layout.addLayout(field_row)

        self.ft_face_mesh_layout.addWidget(row)
        self.ft_face_mesh_entries.append({"widget": row, "field": field})
        if self.ft_minus_btn:
            self.ft_minus_btn.setVisible(len(self.ft_face_mesh_entries) >= 2)

    def _remove_face_mesh_entry(self):
        if len(self.ft_face_mesh_entries) <= 1:
            return
        entry = self.ft_face_mesh_entries.pop()
        entry["widget"].deleteLater()
        self.ft_minus_btn.setVisible(len(self.ft_face_mesh_entries) >= 2)

    # ------------------------------------------------------------------
    # Color Picker Helpers
    # ------------------------------------------------------------------

    def _pick_color(self, btn):
        r, g, b = btn._color
        color = QColorDialog.getColor(
            QColor(int(r * 255), int(g * 255), int(b * 255)), self)
        if color.isValid():
            btn._color = (color.redF(), color.greenF(), color.blueF())
            self._update_color_button(btn)

    def _update_color_button(self, btn):
        r, g, b = btn._color
        btn.setStyleSheet(
            "background-color: rgb({},{},{}); min-width: 60px; "
            "min-height: 20px; border: 1px solid #555; "
            "border-radius: 3px;".format(
                int(r * 255), int(g * 255), int(b * 255)))

    # ------------------------------------------------------------------
    # Confirm Dialog Helper
    # ------------------------------------------------------------------

    def _confirm_dialog(self, title, message, buttons=None):
        """Show a dialog. Returns the clicked button label string."""
        if buttons is None:
            buttons = ["OK"]
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        btn_objs = {}
        for i, label in enumerate(buttons):
            role = (QMessageBox.AcceptRole if i == 0
                    else QMessageBox.RejectRole)
            b = msg.addButton(label, role)
            btn_objs[label] = b
            if i == 0:
                msg.setDefaultButton(b)
        msg.exec_()
        clicked = msg.clickedButton()
        for label, b in btn_objs.items():
            if b == clicked:
                return label
        return buttons[0]

    # ------------------------------------------------------------------
    # Tab Helpers
    # ------------------------------------------------------------------

    def _on_tab_changed(self, index):
        if index < 3:
            self._last_export_tab = [
                TAB_CAMERA_TRACK, TAB_MATCHMOVE, TAB_FACE_TRACK][index]

    def _get_active_tab(self):
        """Return the active export tab identifier."""
        idx = self.tab_widget.currentIndex()
        if idx == 0:
            self._last_export_tab = TAB_CAMERA_TRACK
            return TAB_CAMERA_TRACK
        elif idx == 1:
            self._last_export_tab = TAB_MATCHMOVE
            return TAB_MATCHMOVE
        elif idx == 2:
            self._last_export_tab = TAB_FACE_TRACK
            return TAB_FACE_TRACK
        # Tab 3 = Playblast Settings — use context menu selection
        if self.pb_context_menu:
            ctx = self.pb_context_menu.currentText()
            if ctx == "Camera Track":
                return TAB_CAMERA_TRACK
            elif ctx == "Matchmove":
                return TAB_MATCHMOVE
            elif ctx == "Face Track":
                return TAB_FACE_TRACK
        return None

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _browse_export_root(self):
        result = QFileDialog.getExistingDirectory(
            self, "Select Export Root Directory")
        if result:
            self.export_root_field.setText(result)

    def _browse_stmap(self, target_field):
        result = QFileDialog.getOpenFileName(
            self, "Select STMap EXR", "",
            "EXR Files (*.exr);;All Files (*)")
        if isinstance(result, (list, tuple)):
            result = result[0]
        if result:
            target_field.setText(result)

    def _load_selection_into(self, target_field, role):
        """Validate the current selection and load it into a QLineEdit."""
        if target_field.text().strip():
            target_field.setText("")
            return

        sel = cmds.ls(selection=True, long=False)
        if not sel:
            self._confirm_dialog(
                "No Selection",
                "Export Genie {}\n\nNothing is selected. "
                "Please select an object first.".format(TOOL_VERSION))
            return

        obj = sel[0]

        if role == "camera":
            shapes = cmds.listRelatives(
                obj, shapes=True, type="camera") or []
            if not shapes:
                if cmds.nodeType(obj) == "camera":
                    parents = cmds.listRelatives(obj, parent=True)
                    if parents:
                        obj = parents[0]
                else:
                    self._confirm_dialog(
                        "Invalid Selection",
                        "Export Genie {}\n\n'{}' is not a camera. "
                        "Please select a camera.".format(
                            TOOL_VERSION, obj))
                    return
        else:
            if cmds.nodeType(obj) != "transform":
                role_labels = {
                    "geo": "geo group/root",
                    "rig": "rig root",
                    "proxy": "static geo root",
                }
                self._confirm_dialog(
                    "Invalid Selection",
                    "Export Genie {}\n\n'{}' is not a transform node. "
                    "Please select the {}.".format(
                        TOOL_VERSION, obj,
                        role_labels.get(role, role)))
                return

        target_field.setText(obj)

        if role == "camera":
            self._set_frame_range_from_camera(obj)

    def _set_frame_range_from_camera(self, cam_xform):
        """Set start/end frames from the camera's animation curve extents."""
        keys = []
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

        for n in nodes_to_check:
            anim_curves = cmds.listConnections(
                n, source=True, destination=False,
                type="animCurve") or []
            for ac in anim_curves:
                ac_keys = cmds.keyframe(
                    ac, query=True, timeChange=True) or []
                keys.extend(ac_keys)

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
            self.start_frame_spin.setValue(first_frame)
            self.end_frame_spin.setValue(last_frame)

    def _load_selection(self, tab_prefix, role):
        """Load the current viewport selection into the appropriate field."""
        if tab_prefix == "ct":
            first_cam = (self.ct_camera_entries[0]["field"]
                         if self.ct_camera_entries else None)
            field_map = {"camera": first_cam}
        elif tab_prefix == "ft":
            first_ft_cam = (self.ft_camera_entries[0]["field"]
                            if self.ft_camera_entries else None)
            first_ft_sg = (self.ft_static_geo_entries[0]["field"]
                           if self.ft_static_geo_entries else None)
            field_map = {
                "camera": first_ft_cam,
                "proxy": first_ft_sg,
            }
        else:
            first_mm_cam = (self.mm_camera_entries[0]["field"]
                            if self.mm_camera_entries else None)
            field_map = {"camera": first_mm_cam}

        target_field = field_map.get(role)
        if not target_field:
            return
        self._load_selection_into(target_field, role)

    def _set_timeline_range(self):
        start = cmds.playbackOptions(query=True, animationStartTime=True)
        end = cmds.playbackOptions(query=True, animationEndTime=True)
        self.start_frame_spin.setValue(int(start))
        self.end_frame_spin.setValue(int(end))

    def _on_tpose_toggled(self, checked):
        pass

    def _on_tpose_frame_changed(self, value):
        pass

    def _refresh_scene_info(self):
        scene_path = cmds.file(query=True, sceneName=True)
        if scene_path:
            scene_short = cmds.file(
                query=True, sceneName=True, shortName=True)
            self.scene_info_label.setText("Scene: " + scene_short)
            # Auto-populate export folder with filename (no extension)
            clean = VersionParser._strip_increment(scene_short)
            folder_name = os.path.splitext(clean)[0]
            self.export_name_field.setText(folder_name)
            self.export_root_field.setPlaceholderText(folder_name)
        else:
            self.scene_info_label.setText("Scene: (unsaved scene)")
            self.export_root_field.setPlaceholderText("")

    def _log(self, message):
        self.log_field.append(message)
        self.log_field.moveCursor(QTextCursor.End)

    def _log_result(self, label, success):
        """Append a single-line task result to the log.

        success=True  -> 'MA complete.'
        success=False -> 'MA failed. See Script Editor.'
        """
        if success:
            self._log("{} complete.".format(label))
        else:
            self._log("{} failed. See Script Editor.".format(label))

    # ------------------------------------------------------------------
    # Progress Bar
    # ------------------------------------------------------------------

    def _widget_alive(self, widget):
        """Return True if a Qt widget's C++ object still exists."""
        try:
            widget.isVisible()
            return True
        except RuntimeError:
            return False

    def _reset_progress(self, total_steps):
        self._progress_total = max(total_steps, 1)
        self._progress_done = 0
        try:
            if self._widget_alive(self.progress_bar):
                self.progress_bar.setValue(0)
                self.progress_bar.setVisible(True)
            if self._widget_alive(self.progress_label):
                self.progress_label.setText("0%")
                self.progress_label.setVisible(True)
            cmds.refresh(force=True)
        except Exception:
            pass

    def _advance_progress(self):
        self._progress_done += 1
        pct = int(
            (self._progress_done / float(self._progress_total)) * 100)
        try:
            if self._widget_alive(self.progress_bar):
                self.progress_bar.setValue(min(pct, 100))
            if self._widget_alive(self.progress_label):
                self.progress_label.setText("{}%".format(
                    min(pct, 100)))
            cmds.refresh(force=True)
        except Exception:
            pass

    def _hide_progress(self):
        try:
            if self._widget_alive(self.progress_bar):
                self.progress_bar.setVisible(False)
            if self._widget_alive(self.progress_label):
                self.progress_label.setVisible(False)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_shared(self):
        errors = []
        warnings = []

        scene_path = cmds.file(query=True, sceneName=True)
        if not scene_path:
            errors.append("Scene has not been saved. Please save first.")

        export_root = self.export_root_field.text().strip()
        if not export_root:
            errors.append("Export root directory is not set.")
        elif not os.path.isdir(export_root):
            errors.append(
                "Export root directory does not exist:\n" + export_root)

        start_frame = self.start_frame_spin.value()
        end_frame = self.end_frame_spin.value()
        if end_frame <= start_frame:
            errors.append("End frame must be greater than start frame.")

        # Parse folder name into base + version
        folder_name = self.export_name_field.text().strip()
        if not folder_name:
            errors.append("Export Folder is not set.")
            scene_base = ""
            version_str = "v01"
        else:
            scene_base, version_str = VersionParser.parse_folder_name(
                folder_name)

        return (errors, warnings, export_root, version_str, scene_base,
                folder_name, start_frame, end_frame)

    def _validate_camera_track(self):
        errors, warnings, export_root, version_str, scene_base, \
            folder_name, start_frame, end_frame = self._validate_shared()

        do_ma = self.ct_ma_checkbox.isChecked()
        do_jsx = self.ct_jsx_checkbox.isChecked()
        do_fbx = self.ct_fbx_checkbox.isChecked()
        do_abc = self.ct_abc_checkbox.isChecked()
        do_usd = self.ct_usd_checkbox.isChecked()
        do_mov = self.ct_mov_checkbox.isChecked()
        if not (do_ma or do_jsx or do_fbx or do_abc or do_usd or do_mov):
            errors.append("No export format selected.")

        cameras = []
        for i, entry in enumerate(self.ct_camera_entries):
            c = entry["field"].text().strip()
            if c:
                cameras.append(c)
            suffix = "" if i == 0 else " {}".format(i + 1)
            if c and not cmds.objExists(c):
                errors.append(
                    "Camera{} '{}' no longer exists in the "
                    "scene.".format(suffix, c))

        geo_roots = []
        for i, entry in enumerate(self.ct_geo_fields):
            g = entry["field"].text().strip()
            if g:
                geo_roots.append(g)
            suffix = "" if i == 0 else " {}".format(i + 1)
            if g and not cmds.objExists(g):
                errors.append(
                    "Geo Group{} '{}' no longer exists in the scene.".format(
                        suffix, g))

        obj_tracks = []
        for i, entry in enumerate(self.ct_obj_track_entries):
            o = entry["field"].text().strip()
            if o:
                obj_tracks.append(o)
            suffix = "" if i == 0 else " {}".format(i + 1)
            if o and not cmds.objExists(o):
                errors.append(
                    "Object Track{} '{}' no longer exists in the "
                    "scene.".format(suffix, o))

        has_cameras = bool(cameras)
        has_geo = bool(geo_roots or obj_tracks)
        if do_ma and not has_cameras and not has_geo:
            errors.append(
                "MA export enabled but no Camera or Geo Node assigned.")
        if do_jsx and not has_cameras and not has_geo:
            errors.append(
                "JSX export enabled but no Camera or Geo Node assigned.")
        if do_fbx and not (has_cameras or has_geo):
            errors.append(
                "FBX export enabled but no Camera or Geo Node assigned.")
        if do_abc and not (has_cameras or has_geo):
            errors.append(
                "Alembic export enabled but no Camera or Geo Node assigned.")
        if do_usd and not (has_cameras or has_geo):
            errors.append(
                "USD export enabled but no Camera or Geo Node assigned.")

        assigned = []
        for i, c in enumerate(cameras):
            suffix = "" if i == 0 else " {}".format(i + 1)
            assigned.append(("Camera{}".format(suffix), c))
        for i, g in enumerate(geo_roots):
            suffix = "" if i == 0 else " {}".format(i + 1)
            assigned.append(("Geo Group{}".format(suffix), g))
        for i, o in enumerate(obj_tracks):
            suffix = "" if i == 0 else " {}".format(i + 1)
            assigned.append(("Object Track{}".format(suffix), o))
        self._check_name_collisions(errors, assigned)

        if do_jsx and geo_roots:
            all_jsx_children = []
            for g in geo_roots:
                if not g or not cmds.objExists(g):
                    continue
                children = cmds.listRelatives(
                    g, children=True, type="transform") or []
                if not children:
                    gr_long = cmds.ls(g, long=True)
                    children = gr_long if gr_long else [g]
                for cam in cameras:
                    children = [
                        c for c in children
                        if not Exporter._is_descendant_of(cam, c)]
                children = [
                    c for c in children
                    if "chisels" not in c.lower()
                    and "nulls" not in c.lower()]
                all_jsx_children.extend(children)
            name_count = {}
            for c in all_jsx_children:
                short = c.rsplit("|", 1)[-1].rsplit(":", 1)[-1]
                name_count.setdefault(short, []).append(c)
            for short, nodes in name_count.items():
                if len(nodes) > 1:
                    errors.append(
                        "Name collision: Multiple geo children share "
                        "the name '{}'. OBJ files would overwrite "
                        "each other. Please rename them to be "
                        "unique.".format(short))

        return errors, warnings

    def _validate_matchmove(self):
        errors, warnings, export_root, version_str, scene_base, \
            folder_name, start_frame, end_frame = self._validate_shared()

        do_ma = self.mm_ma_checkbox.isChecked()
        do_fbx = self.mm_fbx_checkbox.isChecked()
        do_abc = self.mm_abc_checkbox.isChecked()
        do_usd = self.mm_usd_checkbox.isChecked()
        do_mov = self.mm_mov_checkbox.isChecked()
        if not (do_ma or do_fbx or do_abc or do_usd or do_mov):
            errors.append("No export format selected.")

        camera = (self.mm_camera_entries[0]["field"].text().strip()
                  if self.mm_camera_entries else "")

        proxy_geos = []
        for i, entry in enumerate(self.mm_static_geo_fields):
            pg = entry["field"].text().strip()
            if pg:
                proxy_geos.append(pg)
            suffix = "" if i == 0 else " {}".format(i + 1)
            if pg and not cmds.objExists(pg):
                errors.append(
                    "Static Geo{} '{}' no longer exists in the scene.".format(
                        suffix, pg))

        rig_roots = []
        geo_roots = []
        for i, pair in enumerate(self.mm_rig_geo_pairs):
            r = pair["rig_field"].text().strip()
            g = pair["geo_field"].text().strip()
            if r:
                rig_roots.append(r)
            if g:
                geo_roots.append(g)
            suffix = "" if i == 0 else " {}".format(i + 1)
            if r and not cmds.objExists(r):
                errors.append(
                    "Main Rig Group{} '{}' no longer exists in the "
                    "scene.".format(suffix, r))
            if g and not cmds.objExists(g):
                errors.append(
                    "Mesh Group{} '{}' no longer exists in the "
                    "scene.".format(suffix, g))

        if do_ma and not any(geo_roots + rig_roots + [camera]):
            errors.append(
                "MA export enabled but no roles assigned (nothing to export).")
        if do_fbx and not (geo_roots or rig_roots):
            errors.append(
                "FBX export enabled but no Mesh Group or Main Rig "
                "Group assigned.")
        if do_abc and not (geo_roots or rig_roots):
            errors.append(
                "Alembic export enabled but no Mesh Group or "
                "Main Rig Group assigned.")
        if do_usd and not (geo_roots or rig_roots):
            errors.append(
                "USD export enabled but no Mesh Group or "
                "Main Rig Group assigned.")

        if camera and not cmds.objExists(camera):
            errors.append(
                "Camera '{}' no longer exists in the scene.".format(camera))

        assigned = []
        if camera:
            assigned.append(("Camera", camera))
        for i, pg in enumerate(proxy_geos):
            suffix = "" if i == 0 else " {}".format(i + 1)
            assigned.append(("Static Geo{}".format(suffix), pg))
        for i, pair in enumerate(self.mm_rig_geo_pairs):
            r = pair["rig_field"].text().strip()
            g = pair["geo_field"].text().strip()
            suffix = "" if i == 0 else " {}".format(i + 1)
            if r:
                assigned.append(("Main Rig Group{}".format(suffix), r))
            if g:
                assigned.append(("Mesh Group{}".format(suffix), g))
        self._check_name_collisions(errors, assigned)

        if self.tpose_checkbox.isChecked():
            tpose_frame = self.tpose_frame_spin.value()
            if tpose_frame >= start_frame:
                warnings.append(
                    "T-pose frame ({}) is not before start frame "
                    "({}). The T-pose will not be a distinct frame "
                    "in the export.".format(tpose_frame, start_frame))

        return errors, warnings

    def _validate_face_track(self):
        errors, warnings, export_root, version_str, scene_base, \
            folder_name, start_frame, end_frame = self._validate_shared()

        do_ma = self.ft_ma_checkbox.isChecked()
        do_fbx = self.ft_fbx_checkbox.isChecked()
        do_usd = self.ft_usd_checkbox.isChecked()
        do_mov = self.ft_mov_checkbox.isChecked()
        if not (do_ma or do_fbx or do_usd or do_mov):
            errors.append("No export format selected.")

        camera = (self.ft_camera_entries[0]["field"].text().strip()
                  if self.ft_camera_entries else "")
        static_geo_list = [
            e["field"].text().strip()
            for e in self.ft_static_geo_entries
            if e["field"].text().strip()]
        static_geo = static_geo_list[0] if static_geo_list else ""

        face_meshes = []
        for i, entry in enumerate(self.ft_face_mesh_entries):
            fm = entry["field"].text().strip()
            if fm:
                face_meshes.append(fm)
            suffix = "" if i == 0 else " {}".format(i + 1)
            if fm and not cmds.objExists(fm):
                errors.append(
                    "Face Mesh{} '{}' no longer exists in the "
                    "scene.".format(suffix, fm))

        if do_fbx and not face_meshes:
            errors.append("FBX export enabled but no Face Mesh assigned.")
        if do_usd and not face_meshes:
            errors.append("USD export enabled but no Face Mesh assigned.")
        if do_ma and not any(face_meshes + [camera]):
            errors.append(
                "MA export enabled but no roles assigned (nothing to export).")

        for role_name, value in [
            ("Camera", camera),
            ("Static Geo", static_geo),
        ]:
            if value and not cmds.objExists(value):
                errors.append(
                    "{} '{}' no longer exists in the scene.".format(
                        role_name, value))

        assigned = []
        if camera:
            assigned.append(("Camera", camera))
        if static_geo:
            assigned.append(("Static Geo", static_geo))
        for i, entry in enumerate(self.ft_face_mesh_entries):
            fm = entry["field"].text().strip()
            suffix = "" if i == 0 else " {}".format(i + 1)
            if fm:
                assigned.append(("Face Mesh{}".format(suffix), fm))
        self._check_name_collisions(errors, assigned)

        return errors, warnings

    @staticmethod
    def _check_name_collisions(errors, assigned_nodes):
        seen = {}
        for role, node in assigned_nodes:
            if node in seen:
                errors.append(
                    "Name collision: '{}' is assigned to both {} "
                    "and {}.".format(node, seen[node], role))
            else:
                seen[node] = role

        cameras = [n for r, n in assigned_nodes if "camera" in r.lower()]
        for cam in cameras:
            if cam != "cam_main" and cmds.objExists("cam_main"):
                errors.append(
                    "Name collision: A node named 'cam_main' already "
                    "exists. The camera will be renamed to 'cam_main' "
                    "during export, which would conflict.")
                break

    @staticmethod
    def _check_obj_name_collisions(errors, geo_root, camera):
        children = cmds.listRelatives(
            geo_root, children=True, type="transform") or []
        if not children:
            return
        if camera:
            children = [
                c for c in children
                if not Exporter._is_descendant_of(camera, c)]
        children = [
            c for c in children
            if "chisels" not in c.lower()
            and "nulls" not in c.lower()]
        name_count = {}
        for c in children:
            short = c.rsplit("|", 1)[-1].rsplit(":", 1)[-1]
            name_count.setdefault(short, []).append(c)
        for short, nodes in name_count.items():
            if len(nodes) > 1:
                errors.append(
                    "Name collision: Multiple geo children share the "
                    "name '{}'. OBJ files would overwrite each other. "
                    "Please rename them to be unique.".format(short))

    # ------------------------------------------------------------------
    # Export Orchestration
    # ------------------------------------------------------------------

    def _on_export(self):
        if self._preview_active:
            self._exit_preview_mode()
        self.log_field.clear()

        active_tab = self._get_active_tab()
        if active_tab is None:
            self._confirm_dialog(
                "Export Context Required",
                "Please select an Export Context (Camera Track, "
                "Matchmove, or Face Track) in the Playblast "
                "Settings tab before exporting.")
            return
        if active_tab == TAB_CAMERA_TRACK:
            self._export_camera_track()
        elif active_tab == TAB_MATCHMOVE:
            self._export_matchmove()
        else:
            self._export_face_track()

    # ------------------------------------------------------------------
    # Preview Playblast
    # ------------------------------------------------------------------

    def _on_preview_playblast(self):
        if self._preview_active:
            self._exit_preview_mode()
        else:
            self._enter_preview_mode()

    def _enter_preview_mode(self):
        active_tab = self._get_active_tab()
        if active_tab is None:
            self._confirm_dialog(
                "Export Context Required",
                "Please select an Export Context (Camera Track, "
                "Matchmove, or Face Track) in the Playblast "
                "Settings tab before previewing.")
            return

        if active_tab == TAB_CAMERA_TRACK:
            camera = (self.ct_camera_entries[0]["field"].text().strip()
                      if self.ct_camera_entries else "")
        elif active_tab == TAB_MATCHMOVE:
            camera = (self.mm_camera_entries[0]["field"].text().strip()
                  if self.mm_camera_entries else "")
        else:
            camera = (self.ft_camera_entries[0]["field"].text().strip()
                  if self.ft_camera_entries else "")

        if not camera or not cmds.objExists(camera):
            self._confirm_dialog(
                "Preview Playblast",
                "Export Genie {}\n\n"
                "No valid camera assigned. Please load a "
                "camera in the Node Picker first.".format(TOOL_VERSION))
            return

        self._preview_active = True
        for btn in self._preview_buttons:
            btn.setText("Exit Preview")
            btn.setStyleSheet(
                "background-color: rgb(230, 128, 128); color: white;")
        for hint in self._preview_hints:
            hint.setVisible(True)
        cmds.refresh(currentView=True)

        raw_pb = self.pb_raw_playblast_cb.isChecked()
        custom_vt = self.pb_custom_vt_cb.isChecked()
        far_clip = self.pb_far_clip_spin.value()

        state = {"tab": active_tab, "raw_playblast": raw_pb}

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

        if camera and model_panel:
            state["original_cam"] = cmds.modelPanel(
                model_panel, query=True, camera=True)
            cmds.lookThru(model_panel, camera)
        state["camera"] = camera

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

        if model_panel:
            try:
                state["original_grid"] = cmds.modelEditor(
                    model_panel, query=True, grid=True)
                cmds.modelEditor(model_panel, edit=True, grid=False)
            except Exception:
                pass

        state["original_sel"] = cmds.ls(selection=True)
        cmds.select(clear=True)

        if not raw_pb and model_panel:
            if active_tab == TAB_CAMERA_TRACK:
                self._enter_preview_ct(state, model_panel)
            elif active_tab in (TAB_MATCHMOVE, TAB_FACE_TRACK):
                self._enter_preview_mm_ft(
                    state, active_tab, model_panel, camera)

            if "original_display_lights" not in state:
                try:
                    state["original_flat_lighting"] = cmds.modelEditor(
                        model_panel, query=True, displayLights=True)
                    cmds.modelEditor(
                        model_panel, edit=True, displayLights="flat")
                except Exception:
                    pass

            original_culling = {}
            for mesh in (cmds.ls(type="mesh", long=True) or []):
                try:
                    original_culling[mesh] = cmds.getAttr(
                        mesh + ".backfaceCulling")
                    cmds.setAttr(mesh + ".backfaceCulling", 3)
                except Exception:
                    pass
            state["original_culling"] = original_culling

        if not raw_pb and not custom_vt:
            try:
                exporter = Exporter(self._log)
                exporter._ensure_playblast_raw_srgb()
            except Exception:
                pass

            if model_panel:
                try:
                    state["original_viewTransform"] = cmds.modelEditor(
                        model_panel, query=True, viewTransformName=True)
                except Exception:
                    state["original_viewTransform"] = ""
                vt_names = []
                try:
                    vt_names = (
                        cmds.colorManagementPrefs(
                            query=True,
                            viewTransformNames=True) or [])
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
        wf_shader = self.pb_wireframe_shader_cb.isChecked()
        aa16 = self.pb_aa16_cb.isChecked()
        geo_roots = []
        for entry in self.ct_geo_fields:
            g = entry["field"].text().strip()
            if g:
                geo_roots.append(g)

        if wf_shader and geo_roots:
            state["original_display"] = cmds.modelEditor(
                model_panel, query=True, displayAppearance=True)
            cmds.modelEditor(
                model_panel, edit=True,
                displayAppearance="smoothShaded")
            state["original_ct_wos"] = cmds.modelEditor(
                model_panel, query=True, wireframeOnShaded=True)
            cmds.modelEditor(
                model_panel, edit=True, wireframeOnShaded=True)

            bg_shader = cmds.shadingNode(
                "useBackground", asShader=True,
                name="mme_ctBgShader_mtl")
            bg_sg = cmds.sets(
                renderable=True, noSurfaceShader=True,
                empty=True, name="mme_ctBgShader_SG")
            cmds.connectAttr(
                "{}.outColor".format(bg_shader),
                "{}.surfaceShader".format(bg_sg), force=True)
            state["ct_bg_shader_nodes"] = [bg_shader, bg_sg]

            ct_meshes = []
            wf_geo_list = (geo_roots if isinstance(geo_roots, list)
                           else [geo_roots])
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
            state["original_display"] = cmds.modelEditor(
                model_panel, query=True, displayAppearance=True)
            if state["original_display"] != "wireframe":
                cmds.modelEditor(
                    model_panel, edit=True,
                    displayAppearance="wireframe")

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
        aa16 = self.pb_aa16_cb.isChecked()
        chk_scale = self.pb_checker_scale_spin.value()
        chk_color = self.pb_checker_color_btn._color
        chk_opacity = self.pb_checker_opacity_spin.value()
        if active_tab == TAB_MATCHMOVE:
            geo_roots = []
            for pair in self.mm_rig_geo_pairs:
                g = pair["geo_field"].text().strip()
                if g:
                    geo_roots.append(g)
        else:
            geo_roots = []
            for entry in self.ft_face_mesh_entries:
                fm = entry["field"].text().strip()
                if fm:
                    geo_roots.append(fm)

        matchmove_geo = [
            g for g in geo_roots if g and cmds.objExists(g)]

        if not matchmove_geo:
            return

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

        state["original_image_plane"] = cmds.modelEditor(
            model_panel, query=True, imagePlane=True)
        cmds.modelEditor(model_panel, edit=True, imagePlane=True)

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

        state["original_mm_display"] = cmds.modelEditor(
            model_panel, query=True, displayAppearance=True)
        cmds.modelEditor(
            model_panel, edit=True,
            displayAppearance="smoothShaded")
        state["original_mm_wos"] = cmds.modelEditor(
            model_panel, query=True, wireframeOnShaded=True)
        cmds.modelEditor(
            model_panel, edit=True, wireframeOnShaded=False)

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
        motion_blur = self.pb_motion_blur_cb.isChecked()
        try:
            state["original_mm_motion_blur"] = cmds.getAttr(
                "hardwareRenderingGlobals.motionBlurEnable")
            cmds.setAttr(
                "hardwareRenderingGlobals.motionBlurEnable", motion_blur)
        except Exception:
            pass

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
                "{}.surfaceShader".format(chk_sg), force=True)

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
                "{}.uvCoord".format(chk_tex), force=True)
            cmds.connectAttr(
                "{}.outUvFilterSize".format(chk_place),
                "{}.uvFilterSize".format(chk_tex), force=True)
            cmds.connectAttr(
                "{}.outColor".format(chk_tex),
                "{}.color".format(chk_lambert), force=True)

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
        state = self._preview_state
        if not state:
            self._preview_active = False
            return

        model_panel = state.get("model_panel")
        camera = state.get("camera")
        active_tab = state.get("tab")
        raw_pb = state.get("raw_playblast", False)

        if not raw_pb and model_panel:
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

            elif active_tab in (TAB_MATCHMOVE, TAB_FACE_TRACK):
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
                try:
                    cmds.isolateSelect(
                        model_panel,
                        state=state.get(
                            "original_isolate_state", False))
                except Exception:
                    pass
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
            if "original_viewTransform" in state:
                try:
                    cmds.modelEditor(
                        model_panel, edit=True,
                        viewTransformName=state[
                            "original_viewTransform"])
                except Exception:
                    pass

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

        self._preview_state = {}
        self._preview_active = False
        for btn in self._preview_buttons:
            btn.setText("Preview Playblast")
            btn.setStyleSheet("")
        for hint in self._preview_hints:
            hint.setVisible(False)

    # ------------------------------------------------------------------
    # Export Pipelines
    # ------------------------------------------------------------------

    def _export_camera_track(self):
        errors, warnings = self._validate_camera_track()
        if errors:
            for e in errors:
                self._log(e)
            self._confirm_dialog(
                "Export Errors",
                "Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(errors)))
            return

        if warnings:
            result = self._confirm_dialog(
                "Warnings",
                "Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(warnings)),
                ["Continue", "Cancel"])
            if result == "Cancel":
                self._log("Export cancelled by user.")
                return

        original_sel = cmds.ls(selection=True)

        export_root = self.export_root_field.text().strip()
        cameras = []
        for entry in self.ct_camera_entries:
            c = entry["field"].text().strip()
            if c:
                cameras.append(c)
        geo_roots = []
        for entry in self.ct_geo_fields:
            g = entry["field"].text().strip()
            if g:
                geo_roots.append(g)
        obj_tracks = []
        for entry in self.ct_obj_track_entries:
            o = entry["field"].text().strip()
            if o:
                obj_tracks.append(o)
        do_ma = self.ct_ma_checkbox.isChecked()
        do_jsx = self.ct_jsx_checkbox.isChecked()
        do_fbx = self.ct_fbx_checkbox.isChecked()
        do_abc = self.ct_abc_checkbox.isChecked()
        do_usd = self.ct_usd_checkbox.isChecked()
        do_mov = self.ct_mov_checkbox.isChecked()
        stmap_undistort = (self.ct_stmap_undistort_field.text().strip()
                          if self.ct_stmap_undistort_field else "")
        stmap_redistort = (self.ct_stmap_redistort_field.text().strip()
                          if self.ct_stmap_redistort_field else "")
        start_frame = self.start_frame_spin.value()
        end_frame = self.end_frame_spin.value()

        folder_name = self.export_name_field.text().strip()
        scene_base, version_str = VersionParser.parse_folder_name(
            folder_name)

        FolderManager.resolve_versioned_dir(
            export_root, scene_base, version_str)
        main_dir = os.path.join(export_root, folder_name)
        FolderManager.resolve_ae_dir(main_dir, scene_base, version_str)

        self._log("Exporting to: {}".format(main_dir))

        exporter = Exporter(self._log)
        results = {}
        all_paths = {}

        total_formats = sum([do_ma, do_fbx, do_abc, do_usd, do_mov])
        if do_jsx:
            total_formats += 2
        self._reset_progress(total_formats)

        # --- Prepare cameras: rename and bake each one ---
        renamed_cams = {}  # current_name -> original_name
        baked_abc_cams = []
        primary_camera = None
        try:
            resolved_cameras = []
            for cam_orig in cameras:
                cam = cam_orig
                if cmds.objExists(cam):
                    short = cam.rsplit("|", 1)[-1].rsplit(
                        ":", 1)[-1]
                    # First camera becomes cam_main; extras keep
                    # their names so all exports include every camera.
                    if not resolved_cameras:
                        if short != "cam_main":
                            new_name = cmds.rename(cam, "cam_main")
                            renamed_cams[new_name] = cam_orig
                            cam = new_name
                    resolved_cameras.append(cam)
                elif not resolved_cameras and cmds.objExists("cam_main"):
                    resolved_cameras.append("cam_main")
                else:
                    self._log(
                        "Camera '{}' not found.".format(cam_orig))
            cameras = resolved_cameras
            primary_camera = cameras[0] if cameras else None

            # Bake Alembic-driven cameras
            for cam in cameras:
                if not cmds.objExists(cam):
                    continue
                cam_shapes = cmds.listRelatives(
                    cam, shapes=True, type="camera") or []
                abc_nodes = set()
                for attr in ("tx", "ty", "tz", "rx", "ry", "rz",
                             "sx", "sy", "sz"):
                    conns = cmds.listConnections(
                        "{}.{}".format(cam, attr),
                        source=True, destination=False) or []
                    for cn in conns:
                        if cmds.nodeType(cn) == "AlembicNode":
                            abc_nodes.add(cn)
                for shp in cam_shapes:
                    conns = cmds.listConnections(
                        "{}.focalLength".format(shp),
                        source=True, destination=False) or []
                    for cn in conns:
                        if cmds.nodeType(cn) == "AlembicNode":
                            abc_nodes.add(cn)
                if not abc_nodes:
                    continue
                self._log("Baking Alembic camera '{}'...".format(cam))
                cmds.undoInfo(openChunk=True)
                baked_abc_cams.append(cam)
                trs = ["tx", "ty", "tz", "rx", "ry", "rz",
                       "sx", "sy", "sz"]
                for a in trs:
                    try:
                        cmds.setAttr(
                            "{}.{}".format(cam, a),
                            lock=False, keyable=True,
                            channelBox=True)
                    except Exception:
                        pass
                cmds.bakeResults(
                    cam,
                    t=(int(start_frame), int(end_frame)),
                    at=trs, simulation=True,
                    preserveOutsideKeys=True)
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
                        at=["focalLength"], simulation=True,
                        preserveOutsideKeys=True)
                all_plugs = [
                    "{}.{}".format(cam, a) for a in trs]
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
                        cam, len(abc_nodes)))

            # Extra cameras beyond the first are passed alongside
            # geo_roots so every export function includes them in its
            # selection.  The primary camera is the first entry and
            # gets passed via the dedicated ``camera`` parameter
            # (used for image-plane gathering, descendant checks, and
            # playblast look-through).
            # Bake Alembic-driven object tracks
            # Bake Alembic-driven object tracks.
            # The user selects a group; we need to bake every
            # descendant transform that is driven by an AlembicNode.
            baked_obj_tracks = []
            for obj in obj_tracks:
                if not cmds.objExists(obj):
                    continue
                # Collect the group itself plus all descendant
                # transforms
                descendants = cmds.listRelatives(
                    obj, allDescendents=True,
                    type="transform", fullPath=True) or []
                nodes_to_check = [obj] + descendants

                nodes_to_bake = []
                trs = ["tx", "ty", "tz", "rx", "ry", "rz",
                       "sx", "sy", "sz"]
                for node in nodes_to_check:
                    # Bake any node whose TRS is driven by
                    # something other than animCurves (Alembic,
                    # constraints, expressions, etc.)
                    has_driver = False
                    for attr in trs:
                        conns = cmds.listConnections(
                            "{}.{}".format(node, attr),
                            source=True,
                            destination=False) or []
                        for cn in conns:
                            nt = cmds.nodeType(cn)
                            if not nt.startswith("animCurve"):
                                has_driver = True
                                break
                        if has_driver:
                            break
                    if has_driver:
                        nodes_to_bake.append(node)

                if not nodes_to_bake:
                    continue

                self._log(
                    "Baking object track '{}' "
                    "({} node(s))...".format(
                        obj, len(nodes_to_bake)))
                cmds.undoInfo(openChunk=True)
                baked_obj_tracks.append(obj)

                for node in nodes_to_bake:
                    for a in trs:
                        try:
                            cmds.setAttr(
                                "{}.{}".format(node, a),
                                lock=False, keyable=True,
                                channelBox=True)
                        except Exception:
                            pass
                    cmds.bakeResults(
                        node,
                        t=(int(start_frame), int(end_frame)),
                        at=trs, simulation=True,
                        preserveOutsideKeys=True)
                    for plug in [
                            "{}.{}".format(node, a) for a in trs]:
                        conns = cmds.listConnections(
                            plug, source=True,
                            destination=False,
                            plugs=True,
                            skipConversionNodes=True) or []
                        for src_plug in conns:
                            src_node = src_plug.split(".")[0]
                            if cmds.nodeType(
                                    src_node).startswith(
                                    "animCurve"):
                                continue
                            try:
                                cmds.disconnectAttr(
                                    src_plug, plug)
                            except Exception:
                                pass

                sys.stderr.write(
                    "[ExportGenie] Baked object track: {} "
                    "({} transform(s)).\n".format(
                        obj, len(nodes_to_bake)))

            extra_cameras = cameras[1:]
            export_geo = extra_cameras + obj_tracks + geo_roots

            if do_jsx:
                geo_children = []
                for gr in geo_roots + obj_tracks:
                    children = cmds.listRelatives(
                        gr, children=True, type="transform",
                        fullPath=True) or []
                    if children:
                        geo_children.extend(children)
                    else:
                        gr_long = cmds.ls(gr, long=True)
                        geo_children.extend(
                            gr_long if gr_long else [gr])
                for cam in cameras:
                    geo_children = [
                        c for c in geo_children
                        if not Exporter._is_descendant_of(cam, c)]
                geo_children = [
                    c for c in geo_children
                    if "chisels" not in c.lower()
                    and "nulls" not in c.lower()]

                ae_paths = FolderManager.build_ae_export_paths(
                    export_root, scene_base, version_str, geo_children,
                    folder_name=folder_name)
                FolderManager.ensure_ae_directories(ae_paths)
                all_paths["jsx"] = ae_paths["jsx"]
                self._advance_progress()

                self._log("Exporting JSX + OBJ...")
                results["jsx"] = exporter.export_jsx(
                    ae_paths["jsx"], ae_paths["obj"],
                    primary_camera,
                    geo_children, start_frame, end_frame,
                    stmap_undistort, stmap_redistort)
                self._log_result("JSX + OBJ", results["jsx"])
                self._advance_progress()

            if do_ma:
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str, tag="cam",
                    folder_name=folder_name)
                FolderManager.ensure_directories({"ma": paths["ma"]})
                all_paths["ma"] = paths["ma"]
                self._log("Exporting MA...")
                results["ma"] = exporter.export_ma(
                    paths["ma"], primary_camera,
                    export_geo, [], [],
                    start_frame=start_frame, end_frame=end_frame)
                self._log_result("MA", results["ma"])
                self._advance_progress()

            if do_fbx:
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str, tag="cam",
                    folder_name=folder_name)
                FolderManager.ensure_directories({"fbx": paths["fbx"]})
                all_paths["fbx"] = paths["fbx"]
                self._log("Exporting FBX...")
                results["fbx"] = exporter.export_fbx(
                    paths["fbx"], primary_camera,
                    export_geo, [], [],
                    start_frame, end_frame)
                self._log_result("FBX", results["fbx"])
                self._advance_progress()

            if do_abc:
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str, tag="cam",
                    folder_name=folder_name)
                FolderManager.ensure_directories({"abc": paths["abc"]})
                all_paths["abc"] = paths["abc"]
                self._log("Exporting ABC...")
                results["abc"] = exporter.export_abc(
                    paths["abc"], primary_camera,
                    export_geo, [],
                    start_frame, end_frame)
                self._log_result("ABC", results["abc"])
                self._advance_progress()

            if do_usd:
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str, tag="cam",
                    folder_name=folder_name)
                FolderManager.ensure_directories({"usd": paths["usd"]})
                all_paths["usd"] = paths["usd"]
                self._log("Exporting USD...")
                results["usd"] = exporter.export_usd(
                    paths["usd"], primary_camera,
                    export_geo, [],
                    start_frame, end_frame)
                self._log_result("USD", results["usd"])
                self._advance_progress()

            if do_mov:
                paths = FolderManager.build_export_paths(
                    export_root, scene_base, version_str, tag="cam",
                    folder_name=folder_name)
                png_mode = False
                mp4_mode = True
                if not Exporter._find_ffmpeg():
                    self._log(
                        "Playblast skipped \u2014 ffmpeg not found.")
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
                    self._log("Exporting Playblast...")
                    raw_pb = self.pb_raw_playblast_cb.isChecked()
                    custom_vt = self.pb_custom_vt_cb.isChecked()
                    wf_shader = self.pb_wireframe_shader_cb.isChecked()
                    aa16 = self.pb_aa16_cb.isChecked()
                    far_clip = self.pb_far_clip_spin.value()
                    show_hud = self.pb_hud_overlay_cb.isChecked()
                    ct_res = Exporter._get_image_plane_resolution(
                        primary_camera)
                    results["mov"] = exporter.export_playblast(
                        pb_path, primary_camera,
                        start_frame, end_frame,
                        camera_track_mode=True,
                        raw_playblast=raw_pb,
                        render_raw_srgb=not custom_vt,
                        wireframe_shader=wf_shader,
                        wireframe_shader_geo=geo_roots,
                        msaa_16=aa16, far_clip=far_clip,
                        png_mode=png_mode, mp4_mode=mp4_mode,
                        mp4_output=paths.get("mp4"),
                        show_hud=show_hud,
                        resolution=ct_res)
                    self._log_result("Playblast", results["mov"])
                self._advance_progress()
        finally:
            # Undo bakes in reverse order (object tracks first,
            # then cameras — reverse of the order they were opened)
            for _ in baked_obj_tracks:
                try:
                    cmds.undoInfo(closeChunk=True)
                except Exception:
                    pass
                try:
                    cmds.undo()
                except Exception:
                    self._log(
                        "Undo object track bake failed. "
                        "See Script Editor.")
            for _ in baked_abc_cams:
                try:
                    cmds.undoInfo(closeChunk=True)
                except Exception:
                    pass
                try:
                    cmds.undo()
                except Exception:
                    self._log(
                        "Undo camera bake failed. See Script Editor.")
            # Restore renamed cameras
            for current_name, orig_name in renamed_cams.items():
                if cmds.objExists(current_name):
                    try:
                        cmds.rename(current_name, orig_name)
                    except Exception:
                        pass

        self._finish_export(results, all_paths, original_sel)

    def _export_matchmove(self):
        errors, warnings = self._validate_matchmove()
        if errors:
            for e in errors:
                self._log(e)
            self._confirm_dialog(
                "Export Errors",
                "Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(errors)))
            return

        if warnings:
            result = self._confirm_dialog(
                "Warnings",
                "Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(warnings)),
                ["Continue", "Cancel"])
            if result == "Cancel":
                self._log("Export cancelled by user.")
                return

        original_sel = cmds.ls(selection=True)

        export_root = self.export_root_field.text().strip()
        camera = (self.mm_camera_entries[0]["field"].text().strip()
                  if self.mm_camera_entries else "")
        proxy_geos = []
        for entry in self.mm_static_geo_fields:
            pg = entry["field"].text().strip()
            if pg:
                proxy_geos.append(pg)
        rig_roots = []
        geo_roots = []
        for pair in self.mm_rig_geo_pairs:
            r = pair["rig_field"].text().strip()
            g = pair["geo_field"].text().strip()
            if r:
                rig_roots.append(r)
            if g:
                geo_roots.append(g)
        do_ma = self.mm_ma_checkbox.isChecked()
        do_fbx = self.mm_fbx_checkbox.isChecked()
        do_abc = self.mm_abc_checkbox.isChecked()
        do_usd = self.mm_usd_checkbox.isChecked()
        do_mov = self.mm_mov_checkbox.isChecked()
        start_frame = self.start_frame_spin.value()
        end_frame = self.end_frame_spin.value()

        tpose_start = start_frame
        if self.tpose_checkbox.isChecked():
            tpose_frame = self.tpose_frame_spin.value()
            if tpose_frame >= start_frame:
                self._log(
                    "Warning: T-pose frame {} is not before start "
                    "frame {} \u2014 T-pose will not be distinct.".format(
                        tpose_frame, start_frame))
            tpose_start = min(start_frame, tpose_frame)

        folder_name = self.export_name_field.text().strip()
        scene_base, version_str = VersionParser.parse_folder_name(
            folder_name)

        FolderManager.resolve_versioned_dir(
            export_root, scene_base, version_str)

        paths = FolderManager.build_export_paths(
            export_root, scene_base, version_str, tag="charMM",
            folder_name=folder_name)
        FolderManager.ensure_directories(
            {k: v for k, v in paths.items()
             if k not in ("png_dir", "png_file",
                          "mp4_tmp_dir", "mp4_tmp_file",
                          "composite_tmp", "composite_plate",
                          "composite_color", "composite_matte",
                          "composite_crown")})


        dir_path = os.path.dirname(
            paths.get("ma", paths.get("fbx", "")))
        self._log("Exporting to: {}".format(dir_path))

        exporter = Exporter(self._log)
        results = {}

        total_formats = sum([do_ma, do_fbx, do_abc, do_usd, do_mov])
        self._reset_progress(total_formats)

        renamed_cam = None
        original_cam_name = camera
        baked_abc_cam = False
        try:
            if camera:
                if cmds.objExists(camera):
                    short = camera.rsplit("|", 1)[-1].rsplit(
                        ":", 1)[-1]
                    if short == "cam_main":
                        # Already named correctly — no rename
                        pass
                    else:
                        renamed_cam = cmds.rename(
                            camera, "cam_main")
                        camera = renamed_cam
                elif cmds.objExists("cam_main"):
                    camera = "cam_main"
                else:
                    self._log("Camera not found. See Script Editor.")
                    camera = None

            # Detect Alembic-driven camera and bake before exports
            # so that ABC/playblast get valid camera animation even
            # if the source .abc file is missing or on another drive.
            if camera and cmds.objExists(camera):
                cam_shapes = cmds.listRelatives(
                    camera, shapes=True, type="camera") or []
                abc_nodes = set()
                for attr in ("tx", "ty", "tz", "rx", "ry", "rz",
                             "sx", "sy", "sz"):
                    conns = cmds.listConnections(
                        "{}.{}".format(camera, attr),
                        source=True, destination=False) or []
                    for c in conns:
                        if cmds.nodeType(c) == "AlembicNode":
                            abc_nodes.add(c)
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
                    for a in trs:
                        try:
                            cmds.setAttr(
                                "{}.{}".format(camera, a),
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
                    )
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
                    # Disconnect Alembic sources (keep baked
                    # animCurves)
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
                                cmds.disconnectAttr(
                                    src_plug, plug)
                            except Exception:
                                pass
                    sys.stderr.write(
                        "[ExportGenie] Baked Alembic camera: {} "
                        "({} AlembicNode(s) disconnected).\n"
                        .format(camera, len(abc_nodes)))

            # Unlock any locked locators in the export groups so that
            # FBX/ABC exporters can bake and export their transforms.
            _all_export_roots = geo_roots + rig_roots + proxy_geos
            if camera and cmds.objExists(camera):
                _all_export_roots.append(camera)
            _lock_attrs = [
                "tx", "ty", "tz", "rx", "ry", "rz",
                "sx", "sy", "sz"]
            for root in _all_export_roots:
                if not root or not cmds.objExists(root):
                    continue
                descendants = cmds.listRelatives(
                    root, allDescendents=True,
                    fullPath=True) or []
                all_nodes = (
                    cmds.ls(root, long=True) or []) + descendants
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
                self._log("Exporting MA...")
                results["ma"] = exporter.export_ma(
                    paths["ma"], camera, geo_roots, rig_roots,
                    proxy_geos,
                    start_frame=start_frame, end_frame=end_frame)
                self._log_result("MA", results["ma"])
                self._advance_progress()

            if do_abc:
                self._log("Exporting ABC...")
                results["abc"] = exporter.export_abc(
                    paths["abc"], camera, geo_roots, proxy_geos,
                    tpose_start, end_frame, rig_roots=rig_roots)
                self._log_result("ABC", results["abc"])
                self._advance_progress()

            if do_usd:
                self._log("Exporting USD...")
                results["usd"] = exporter.export_usd(
                    paths["usd"], camera, geo_roots, proxy_geos,
                    tpose_start, end_frame, rig_roots=rig_roots)
                self._log_result("USD", results["usd"])
                self._advance_progress()

            if do_mov:
                png_mode = False
                mp4_mode = True
                if not Exporter._find_ffmpeg():
                    self._log(
                        "Playblast skipped \u2014 ffmpeg not found.")
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
                    self._log("Exporting Playblast...")
                    raw_pb = self.pb_raw_playblast_cb.isChecked()
                    custom_vt = self.pb_custom_vt_cb.isChecked()
                    chk_scale = self.pb_checker_scale_spin.value()
                    chk_color = self.pb_checker_color_btn._color
                    chk_opacity = self.pb_checker_opacity_spin.value()
                    aa16 = self.pb_aa16_cb.isChecked()
                    mb = self.pb_motion_blur_cb.isChecked()
                    far_clip = self.pb_far_clip_spin.value()
                    show_hud = self.pb_hud_overlay_cb.isChecked()
                    results["mov"] = exporter.export_playblast(
                        pb_path, camera, start_frame, end_frame,
                        matchmove_geo=geo_roots,
                        checker_scale=chk_scale,
                        checker_color=chk_color,
                        checker_opacity=chk_opacity,
                        raw_playblast=raw_pb,
                        render_raw_srgb=not custom_vt,
                        msaa_16=aa16, motion_blur=mb,
                        far_clip=far_clip,
                        png_mode=png_mode, mp4_mode=mp4_mode,
                        mp4_output=paths.get("mp4"),
                        show_hud=show_hud,
                        composite_plate_path=paths.get(
                            "composite_plate"),
                        composite_color_path=paths.get(
                            "composite_color"),
                        composite_matte_path=paths.get(
                            "composite_matte"),
                        composite_tmp_dir=paths.get(
                            "composite_tmp"))
                    self._log_result("Playblast", results["mov"])
                self._advance_progress()

            # FBX is last — destructive prep (bake, import refs,
            # strip namespaces) cannot be reliably undone, so we
            # save the scene to a temp file, run the prep + export,
            # then reopen the original to guarantee a clean restore.
            if do_fbx:
                self._log("Exporting FBX...")
                scene_path = cmds.file(
                    query=True, sceneName=True)
                if not scene_path:
                    self._log(
                        "Scene must be saved before FBX export.")
                    results["fbx"] = False
                else:
                    import tempfile
                    tmp_dir = tempfile.mkdtemp(
                        prefix="ExportGenie_fbx_")
                    tmp_scene = os.path.join(
                        tmp_dir, os.path.basename(scene_path))
                    try:
                        # Save current scene state to temp file
                        cmds.file(rename=tmp_scene)
                        cmds.file(save=True, type="mayaAscii"
                                  if tmp_scene.endswith(".ma")
                                  else "mayaBinary")
                        # Restore the original file name in the
                        # title bar (the file on disk is unchanged)
                        cmds.file(rename=scene_path)
                        self._log("Scene snapshot saved.")

                        # Destructive prep on the live scene
                        vertex_anim_set = \
                            exporter.detect_vertex_anim_meshes(
                                geo_roots, tpose_start, end_frame)
                        has_vertex_anim = bool(vertex_anim_set)
                        if has_vertex_anim:
                            sys.stderr.write(
                                "[ExportGenie] Detected {} vertex-"
                                "animated mesh(es) in Mesh "
                                "Group.\n".format(
                                    len(vertex_anim_set)))

                        exporter.prep_for_ue5_fbx_export(
                            geo_roots, rig_roots,
                            tpose_start, end_frame,
                            camera=camera,
                            skip_mesh_xforms=vertex_anim_set)

                        def _resolve_name(name):
                            if not name:
                                return name
                            long_names = cmds.ls(name, long=True)
                            if long_names:
                                return long_names[0]
                            short = name.rsplit(":", 1)[-1]
                            long_names = cmds.ls(
                                short, long=True)
                            if len(long_names) == 1:
                                return long_names[0]
                            if long_names:
                                stripped_tail = "/".join(
                                    seg.rsplit(":", 1)[-1]
                                    for seg in name.split("|")
                                    if seg)
                                for ln in long_names:
                                    ln_tail = "/".join(
                                        seg for seg in
                                        ln.split("|") if seg)
                                    if ln_tail.endswith(
                                            stripped_tail):
                                        return ln
                                return long_names[0]
                            return name

                        base_meshes = []
                        if has_vertex_anim:
                            self._log(
                                "Converting vertex animation...")
                            for old_long in list(vertex_anim_set):
                                resolved = _resolve_name(old_long)
                                conv = \
                                    exporter.convert_abc_to_blendshape(
                                        resolved, tpose_start,
                                        end_frame)
                                base_meshes.append(
                                    conv["base_mesh"])

                        fbx_geo = [_resolve_name(g)
                                   for g in geo_roots]
                        fbx_rigs = [_resolve_name(r)
                                    for r in rig_roots]
                        fbx_proxies = [_resolve_name(p)
                                       for p in proxy_geos]
                        fbx_cam = (_resolve_name(camera)
                                   if camera else camera)
                        results["fbx"] = exporter.export_fbx(
                            paths["fbx"], fbx_cam, fbx_geo,
                            fbx_rigs, fbx_proxies,
                            tpose_start, end_frame,
                            export_input_connections=has_vertex_anim,
                        )
                    except Exception as exc:
                        self._log(
                            "FBX export failed. See Script Editor.")
                        sys.stderr.write(
                            "[ExportGenie] FBX error: "
                            "{}\n".format(exc))
                        results["fbx"] = False
                    finally:
                        # Reopen the pre-export snapshot to
                        # guarantee a clean restore (preserves any
                        # unsaved changes the user had).
                        restored = False
                        try:
                            cmds.file(
                                tmp_scene, open=True, force=True)
                            cmds.file(rename=scene_path)
                            self._log("Scene restored.")
                            restored = True
                        except Exception:
                            pass
                        if not restored:
                            # Snapshot failed — fall back to the
                            # original file on disk.
                            try:
                                cmds.file(
                                    scene_path, open=True,
                                    force=True)
                                self._log(
                                    "Restored from saved file.")
                            except Exception:
                                self._log(
                                    "Scene restore failed! "
                                    "Snapshot at: " + tmp_scene)
                        # Clean up temp file
                        try:
                            if os.path.isfile(tmp_scene):
                                os.remove(tmp_scene)
                            os.rmdir(tmp_dir)
                        except Exception:
                            pass
                self._log_result("FBX", results.get("fbx", False))
                self._advance_progress()

        finally:
            # Undo Alembic camera bake (restores original connections)
            if baked_abc_cam:
                try:
                    cmds.undoInfo(closeChunk=True)
                except Exception:
                    pass
                try:
                    cmds.undo()
                except Exception:
                    self._log(
                        "Undo camera bake failed. "
                        "See Script Editor.")
            # Restore original camera name
            if renamed_cam and cmds.objExists(renamed_cam):
                try:
                    cmds.rename(renamed_cam, original_cam_name)
                except Exception:
                    pass

        self._finish_export(results, paths, original_sel)

    def _export_face_track(self):
        errors, warnings = self._validate_face_track()
        if errors:
            for e in errors:
                self._log(e)
            self._confirm_dialog(
                "Export Errors",
                "Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(errors)))
            return

        if warnings:
            result = self._confirm_dialog(
                "Warnings",
                "Export Genie {}\n\n{}".format(
                    TOOL_VERSION, "\n\n".join(warnings)),
                ["Continue", "Cancel"])
            if result == "Cancel":
                self._log("Export cancelled by user.")
                return

        original_sel = cmds.ls(selection=True)

        export_root = self.export_root_field.text().strip()
        camera = (self.ft_camera_entries[0]["field"].text().strip()
                  if self.ft_camera_entries else "")
        static_geo_list = [
            e["field"].text().strip()
            for e in self.ft_static_geo_entries
            if e["field"].text().strip()]
        static_geo = static_geo_list[0] if static_geo_list else ""
        face_meshes = []
        for entry in self.ft_face_mesh_entries:
            fm = entry["field"].text().strip()
            if fm:
                face_meshes.append(fm)
        do_ma = self.ft_ma_checkbox.isChecked()
        do_fbx = self.ft_fbx_checkbox.isChecked()
        do_usd = self.ft_usd_checkbox.isChecked()
        do_mov = self.ft_mov_checkbox.isChecked()
        start_frame = self.start_frame_spin.value()
        end_frame = self.end_frame_spin.value()

        folder_name = self.export_name_field.text().strip()
        scene_base, version_str = VersionParser.parse_folder_name(
            folder_name)

        FolderManager.resolve_versioned_dir(
            export_root, scene_base, version_str)

        paths = FolderManager.build_export_paths(
            export_root, scene_base, version_str, tag="KTHead",
            folder_name=folder_name)
        FolderManager.ensure_directories(
            {k: v for k, v in paths.items()
             if k not in ("png_dir", "png_file",
                          "mp4_tmp_dir", "mp4_tmp_file",
                          "composite_tmp", "composite_plate",
                          "composite_color", "composite_matte",
                          "composite_crown")})


        dir_path = os.path.dirname(
            paths.get("ma", paths.get("fbx", "")))
        self._log("Exporting to: {}".format(dir_path))

        exporter = Exporter(self._log)
        results = {}

        total_formats = sum([do_ma, do_fbx, do_usd, do_mov])
        self._reset_progress(total_formats)

        renamed_cam = None
        original_cam_name = camera
        baked_abc_cam = False
        try:
            if camera:
                if cmds.objExists(camera):
                    short = camera.rsplit("|", 1)[-1].rsplit(
                        ":", 1)[-1]
                    if short == "cam_main":
                        # Already named correctly — no rename
                        pass
                    else:
                        renamed_cam = cmds.rename(
                            camera, "cam_main")
                        camera = renamed_cam
                elif cmds.objExists("cam_main"):
                    camera = "cam_main"
                else:
                    self._log("Camera not found. See Script Editor.")
                    camera = None

            if camera and cmds.objExists(camera):
                cam_shapes = cmds.listRelatives(
                    camera, shapes=True, type="camera") or []
                abc_nodes = set()
                for attr in ("tx", "ty", "tz", "rx", "ry", "rz",
                             "sx", "sy", "sz"):
                    conns = cmds.listConnections(
                        "{}.{}".format(camera, attr),
                        source=True, destination=False) or []
                    for c in conns:
                        if cmds.nodeType(c) == "AlembicNode":
                            abc_nodes.add(c)
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
                    for a in trs:
                        try:
                            cmds.setAttr(
                                "{}.{}".format(camera, a),
                                lock=False, keyable=True,
                                channelBox=True)
                        except Exception:
                            pass
                    cmds.bakeResults(
                        camera,
                        t=(int(start_frame), int(end_frame)),
                        at=trs, simulation=True,
                        preserveOutsideKeys=True)
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
                            at=["focalLength"], simulation=True,
                            preserveOutsideKeys=True)
                    all_plugs = [
                        "{}.{}".format(camera, a) for a in trs]
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

            if do_mov:
                png_mode = False
                mp4_mode = True
                if not Exporter._find_ffmpeg():
                    self._log(
                        "Playblast skipped \u2014 ffmpeg not found.")
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
                    self._log("Exporting Playblast...")
                    raw_pb = self.pb_raw_playblast_cb.isChecked()
                    custom_vt = self.pb_custom_vt_cb.isChecked()
                    chk_scale = self.pb_checker_scale_spin.value()
                    chk_color = self.pb_checker_color_btn._color
                    chk_opacity = self.pb_checker_opacity_spin.value()
                    aa16 = self.pb_aa16_cb.isChecked()
                    mb = self.pb_motion_blur_cb.isChecked()
                    far_clip = self.pb_far_clip_spin.value()
                    show_hud = self.pb_hud_overlay_cb.isChecked()
                    results["mov"] = exporter.export_playblast(
                        pb_path, camera, start_frame, end_frame,
                        face_track_mode=True,
                        matchmove_geo=face_meshes,
                        checker_scale=chk_scale,
                        checker_color=chk_color,
                        checker_opacity=chk_opacity,
                        raw_playblast=raw_pb,
                        render_raw_srgb=not custom_vt,
                        msaa_16=aa16, motion_blur=mb,
                        far_clip=far_clip,
                        png_mode=png_mode, mp4_mode=mp4_mode,
                        mp4_output=paths.get("mp4"),
                        show_hud=show_hud,
                        composite_plate_path=paths.get(
                            "composite_plate"),
                        composite_color_path=paths.get(
                            "composite_color"),
                        composite_matte_path=paths.get(
                            "composite_matte"),
                        composite_tmp_dir=paths.get(
                            "composite_tmp"))
                    self._log_result("Playblast", results["mov"])
                self._advance_progress()

            # MA, USD, and FBX are last — all require destructive
            # scene changes (import refs, strip namespaces, convert
            # ABC to blendshapes) that cannot be reliably undone.
            # We save the scene to a temp file, run the prep +
            # export, then reopen the original for a clean restore.
            if do_ma or do_usd or do_fbx:
                scene_path = cmds.file(
                    query=True, sceneName=True)
                if not scene_path:
                    self._log(
                        "Scene must be saved before "
                        "MA/USD/FBX export.")
                    if do_ma:
                        results["ma"] = False
                    if do_usd:
                        results["usd"] = False
                    if do_fbx:
                        results["fbx"] = False
                else:
                    import tempfile
                    tmp_dir = tempfile.mkdtemp(
                        prefix="ExportGenie_ft_")
                    tmp_scene = os.path.join(
                        tmp_dir, os.path.basename(scene_path))
                    try:
                        # Save current scene state to temp file
                        cmds.file(rename=tmp_scene)
                        cmds.file(save=True, type="mayaAscii"
                                  if tmp_scene.endswith(".ma")
                                  else "mayaBinary")
                        cmds.file(rename=scene_path)
                        self._log("Scene snapshot saved.")

                        if do_ma:
                            self._log("Exporting MA...")
                            static_geos = (
                                [static_geo] if static_geo else [])
                            try:
                                # Import references
                                all_refs = cmds.ls(
                                    type="reference") or []
                                for ref_node in all_refs:
                                    if ref_node == \
                                            "sharedReferenceNode":
                                        continue
                                    try:
                                        cmds.file(
                                            referenceNode=ref_node,
                                            importReference=True)
                                    except Exception:
                                        pass

                                # Strip namespaces
                                all_ns = cmds.namespaceInfo(
                                    listOnlyNamespaces=True,
                                    recurse=True) or []
                                skip_ns = {"UI", "shared"}
                                all_ns = [ns for ns in all_ns
                                          if ns not in skip_ns]
                                all_ns.sort(key=len, reverse=True)
                                for ns in all_ns:
                                    try:
                                        cmds.namespace(
                                            removeNamespace=ns,
                                            mergeNamespaceWithRoot=True)
                                    except Exception:
                                        pass

                                def _resolve(name):
                                    if not name:
                                        return name
                                    long_names = cmds.ls(
                                        name, long=True)
                                    if long_names:
                                        return long_names[0]
                                    short = name.rsplit(":", 1)[-1]
                                    long_names = cmds.ls(
                                        short, long=True)
                                    if len(long_names) == 1:
                                        return long_names[0]
                                    if len(long_names) > 1:
                                        return long_names[0]
                                    return name

                                resolved_meshes = [
                                    _resolve(fm)
                                    for fm in face_meshes]
                                resolved_statics = [
                                    _resolve(sg)
                                    for sg in static_geos]
                                resolved_cam = (
                                    _resolve(camera)
                                    if camera else camera)

                                ma_prep = \
                                    exporter.prepare_face_track_for_export(
                                        resolved_meshes,
                                        start_frame, end_frame)
                                export_nodes = ma_prep.get(
                                    "select_for_export",
                                    resolved_meshes)
                                results["ma"] = exporter.export_ma(
                                    paths["ma"], resolved_cam,
                                    export_nodes, [],
                                    resolved_statics,
                                    start_frame=start_frame,
                                    end_frame=end_frame)
                            except Exception as exc:
                                self._log(
                                    "MA export failed. "
                                    "See Script Editor.")
                                sys.stderr.write(
                                    "[ExportGenie] MA error: "
                                    "{}\n".format(exc))
                                results["ma"] = False
                            self._log_result(
                                "MA", results.get("ma", False))
                            self._advance_progress()

                            # Reopen scene before USD/FBX (MA
                            # prep was destructive)
                            if do_usd or do_fbx:
                                try:
                                    cmds.file(
                                        scene_path, open=True,
                                        force=True)
                                except Exception:
                                    cmds.file(
                                        tmp_scene, open=True,
                                        force=True)
                                    cmds.file(rename=scene_path)

                        if do_usd:
                            self._log("Exporting USD...")
                            try:
                                usd_prep = \
                                    exporter.prepare_face_track_for_export(
                                        face_meshes, start_frame,
                                        end_frame)
                                if not usd_prep[
                                        "select_for_export"]:
                                    self._log(
                                        "No geometry found to "
                                        "export.")
                                    results["usd"] = False
                                else:
                                    static_geos = (
                                        [static_geo]
                                        if static_geo else [])
                                    results["usd"] = \
                                        exporter.export_usd(
                                            paths["usd"], camera,
                                            usd_prep[
                                                "select_for_export"
                                            ],
                                            static_geos,
                                            start_frame, end_frame)
                            except Exception as exc:
                                self._log(
                                    "USD export failed. "
                                    "See Script Editor.")
                                sys.stderr.write(
                                    "[ExportGenie] USD error: "
                                    "{}\n".format(exc))
                                results["usd"] = False
                            self._log_result(
                                "USD",
                                results.get("usd", False))
                            self._advance_progress()

                            # Reopen scene before FBX (USD prep
                            # was destructive)
                            if do_fbx:
                                try:
                                    cmds.file(
                                        scene_path, open=True,
                                        force=True)
                                except Exception:
                                    cmds.file(
                                        tmp_scene, open=True,
                                        force=True)
                                    cmds.file(rename=scene_path)

                        if do_fbx:
                            self._log("Exporting FBX...")
                            try:
                                prep = \
                                    exporter.prepare_face_track_for_export(
                                        face_meshes, start_frame,
                                        end_frame)
                                if not prep["select_for_export"]:
                                    self._log(
                                        "No geometry found to "
                                        "export.")
                                    results["fbx"] = False
                                else:
                                    static_geos = (
                                        [static_geo]
                                        if static_geo else [])
                                    results["fbx"] = \
                                        exporter.export_fbx(
                                            paths["fbx"], camera,
                                            prep[
                                                "select_for_export"
                                            ],
                                            [], static_geos,
                                            start_frame, end_frame,
                                            export_input_connections=True)
                            except Exception as exc:
                                self._log(
                                    "FBX export failed. "
                                    "See Script Editor.")
                                sys.stderr.write(
                                    "[ExportGenie] FBX error: "
                                    "{}\n".format(exc))
                                results["fbx"] = False
                            self._log_result(
                                "FBX",
                                results.get("fbx", False))
                            self._advance_progress()

                    except Exception as exc:
                        sys.stderr.write(
                            "[ExportGenie] Export error: "
                            "{}\n".format(exc))
                    finally:
                        # Reopen the pre-export snapshot to
                        # guarantee a clean restore (preserves
                        # any unsaved changes the user had).
                        restored = False
                        try:
                            cmds.file(
                                tmp_scene, open=True, force=True)
                            cmds.file(rename=scene_path)
                            self._log("Scene restored.")
                            restored = True
                        except Exception:
                            pass
                        if not restored:
                            try:
                                cmds.file(
                                    scene_path, open=True,
                                    force=True)
                                self._log(
                                    "Restored from saved file.")
                            except Exception:
                                self._log(
                                    "Scene restore failed! "
                                    "Snapshot at: " + tmp_scene)
                        # Clean up temp file
                        try:
                            if os.path.isfile(tmp_scene):
                                os.remove(tmp_scene)
                            os.rmdir(tmp_dir)
                        except Exception:
                            pass

        finally:
            if baked_abc_cam:
                try:
                    cmds.undoInfo(closeChunk=True)
                except Exception:
                    pass
                try:
                    cmds.undo()
                except Exception:
                    self._log(
                        "Undo camera bake failed. See Script Editor.")
            if renamed_cam and cmds.objExists(renamed_cam):
                try:
                    cmds.rename(renamed_cam, original_cam_name)
                except Exception:
                    pass

        self._finish_export(results, paths, original_sel)

    def _finish_export(self, results, paths, original_sel):
        self._hide_progress()

        if original_sel:
            cmds.select(original_sel, replace=True)
        else:
            cmds.select(clear=True)

        failed = [k for k, v in results.items() if not v]
        if failed:
            self._log("Export finished with errors. See Script Editor.")
            self._confirm_dialog(
                "Export Complete (with errors)",
                "Export Genie {}\n\nSome exports failed: {}\n"
                "See Script Editor for details.".format(
                    TOOL_VERSION,
                    ", ".join(f.upper() for f in failed)))
        else:
            self._log("Export complete.")
            self._confirm_dialog(
                "Export Complete",
                "All exports completed successfully!")


# ---------------------------------------------------------------------------
# Entry Points
# ---------------------------------------------------------------------------
def launch():
    """Open the Export Genie UI. Called by the shelf button.

    Aggressively clears all cached versions of the module so the
    latest .py on disk is always used — no restart required.
    """
    import importlib

    # 1. Remove any cached module object
    sys.modules.pop("ExportGenie", None)

    # 2. Invalidate bytecode caches so Python re-reads the .py
    importlib.invalidate_caches()

    # 3. Delete stale .pyc files next to the script
    scripts_dir = os.path.join(
        cmds.internalVar(userAppDir=True), "scripts")
    pyc_cache = os.path.join(scripts_dir, "__pycache__")
    if os.path.isdir(pyc_cache):
        for f in os.listdir(pyc_cache):
            if f.startswith("ExportGenie.") and f.endswith(
                    (".pyc", ".pyo")):
                try:
                    os.remove(os.path.join(pyc_cache, f))
                except Exception:
                    pass

    # 4. Fresh import from disk
    import ExportGenie as _self_mod
    _self_mod._launch_inner()


def _launch_inner():
    """Internal launcher — called after the module has been reloaded."""
    global _ui_instance

    # Tear down existing workspace control if present
    if cmds.workspaceControl(WORKSPACE_CONTROL_NAME, exists=True):
        cmds.deleteUI(WORKSPACE_CONTROL_NAME)

    _ui_instance = ExportGenieWidget()
    _ui_instance.show(
        dockable=True, area="right", floating=False,
        width=440, height=480, retain=False,
        uiScript="import ExportGenie; ExportGenie._restore_ui()",
    )

    # Tab alongside Attribute Editor (falls back to floating if AE closed)
    try:
        cmds.workspaceControl(
            WORKSPACE_CONTROL_NAME, edit=True,
            tabToControl=("AttributeEditor", -1),
            label="Export Genie  {}".format(TOOL_VERSION))
    except Exception:
        pass

    _ui_instance._register_scene_jobs()


def _restore_ui():
    """Called by workspaceControl uiScript to (re)build UI contents."""
    global _ui_instance
    import importlib
    sys.modules.pop("ExportGenie", None)
    importlib.invalidate_caches()
    # Delete stale .pyc files
    _scripts = os.path.join(
        cmds.internalVar(userAppDir=True), "scripts")
    _cache = os.path.join(_scripts, "__pycache__")
    if os.path.isdir(_cache):
        for _f in os.listdir(_cache):
            if _f.startswith("ExportGenie.") and _f.endswith(
                    (".pyc", ".pyo")):
                try:
                    os.remove(os.path.join(_cache, _f))
                except Exception:
                    pass
    import ExportGenie as _self_mod
    importlib.reload(_self_mod)
    cmds.workspaceControl(
        WORKSPACE_CONTROL_NAME, edit=True,
        label="Export Genie  {}".format(_self_mod.TOOL_VERSION))
    _self_mod._ui_instance = ExportGenieWidget()
    _ui_instance = _self_mod._ui_instance

    # Reparent into existing workspace control
    ptr = MQtUtil.findControl(WORKSPACE_CONTROL_NAME)
    if ptr:
        ctrl_widget = wrapInstance(int(ptr), QWidget)
        if ctrl_widget.layout():
            ctrl_widget.layout().addWidget(_ui_instance)

    _ui_instance._register_scene_jobs()




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
            "import sys, importlib, os, maya.cmds\n"
            "sys.modules.pop('ExportGenie', None)\n"
            "importlib.invalidate_caches()\n"
            "_sd = os.path.join("
            "maya.cmds.internalVar(userAppDir=True),"
            "'scripts','__pycache__')\n"
            "[os.remove(os.path.join(_sd,f)) "
            "for f in os.listdir(_sd) "
            "if f.startswith('ExportGenie.') "
            "and f.endswith(('.pyc','.pyo'))] "
            "if os.path.isdir(_sd) else None\n"
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
