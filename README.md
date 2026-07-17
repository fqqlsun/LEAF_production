# GEE-LEAF Production Tool

The **GEE-LEAF (Landscape Evolution And Forecasting) Production Tool** is designed to execute on the Google Earth Engine (GEE) platform. It consists two operational submodules driven by GEE's Sentinel-2 or Landsat data archives:
1. **Biophysical Parameter Mapping:** Generate four core vegetation biophysical parameters (LAI, fCOVER, fAPAR, and Albedo) maps. Run this module using the [LeafProdTool.ipynb](LeafProdTool.ipynb) notebook.
2. **Temporal Composite Image Generation:** Create a cloud-free composite imagery. Run this module using the [MosaicTool.ipynb](MosaicTool.ipynb) notebook.

**Crucial Platform Requirement:**  
> ⚠️ **Platform Dependency Notice:** This tool is strictly designed to operate on the Google Earth Engine platform. It is explicitly **not intended to function as a standalone software package** independent of Google's cloud infrastructure.

---
## Workflow Overview

The operational logic and processing pipeline of the tool are illustrated in the flowchart below:

![GEE-based LEAF Production Tool Flowchart](/wiki_images/flowchart.png)

---

## Key Features

* **Flexible Configuration:** A highly customizable input parameter dictionary allowing users to define diverse, tailored production requirements for both submodules.
* **Seamless Batch Exporting:** Results can be exported in batch mode to either **Google Drive** or **Google Cloud Storage (GCS)**.

---

## Spatial Coverage & Tiling

The tool partitions and processes standard outputs using a systematic tiling framework:
* **Standard Grid:** Outputs are organized into tiles covering a **900 km × 900 km** footprint, adhering strictly to the [CCRS Tile Grid System](/wiki_images/CCRS_tile_grid_system.png).
* **National Scale:** A total of **26 standard tiles** completely encompass the entire Canadian landmass.
* **Custom ROIs:** Users can override the standard grid system by passing a custom polygon geometry to target a specific Region of Interest (ROI).

---

## Product Specifications & Data Formats

The **Biophysical Parameter Mapping Submodule** currently supports the generation of **four core products**. Each generated product tile outputs a separate GeoTIFF file along with two auxiliary context layers: a **Quality Control (QC) map** and an **Acquisition Date map**.

### Data Storage & Scaling Factors
To optimize storage and processing bandwidth, pixel values are stored as **8-bit unsigned integers (`uint8`)** and must be converted back to physical units using product-specific rescaling factors:

| Product | Description | Data Type | Scaling Factor | Physical Range |
| :--- | :--- | :---: | :---: | :---: |
| **LAI** | Leaf Area Index | `uint8` | `20` | $0.0 - 12.75$ |
| **fCOVER** | Fraction of Green Vegetation Cover | `uint8` | `200` | $0.0 - 1.0$ |
| **fAPAR** | Fraction of Absorbed Photosynthetically Active Radiation | `uint8` | `200` | $0.0 - 1.0$ |
| **Albedo** | Surface Albedo | `uint8` | `200` | $0.0 - 1.0$ |

$$\text{Physical Value} = \frac{\text{Digital Number (DN)}}{\text{Scaling Factor}}$$

### Quality Control (QC) Bitmask Structure
The QC map provides pixel-level data lineage and condition tracking via an **8-bit bitmask**. Decode the byte values according to the bit allocation below:

| Bit(s) | Value / Flag | Definition / Condition |
| :---: | :---: | :--- |
| **Bit 0** | `1` | Input data is out of acceptable range |
| **Bit 1** | `1` | Output product is out of physical range |
| **Bit 2** | `1` | Invalid pixel (due to cloud, shadow, snow, ice, water, or sensor saturation) |
| **Bits 3–7** | *Sensor Code* | Identifies the source satellite platform: <br>• `40` = Landsat 5<br>• `56` = Landsat 7<br>• `64` = Landsat 8<br>• `72` = Landsat 9<br>• `168` = Sentinel-2 |

---

## Google Earth Engine (GEE) Access & Compliance

Before deploying or running this software, please note the following platform and legal requirements:

* **User Account Obligation:** Users must independently obtain and maintain their own valid [Google Earth Engine Account](https://earthengine.google.com/). 
* **Terms of Service:** Your utilization of this tool and any subsequent processing jobs are entirely bound by and governed under [Google's Earth Engine Terms of Service](https://earthengine.google.com/terms/).
* **Data & Platform Disclaimer:** Releasing this source code **does not grant** users access to the Google Earth Engine infrastructure, compute allocations, or its underlying spatial datasets. Users are completely responsible for managing their own platform permissions, cloud project billing, and data quotas.

---

## System Requirements

Because the heavy computational lifting (pixel-level map algebra, cloud masking, and hybrid temporal fitting) is executed on Google Earth Engine's cloud servers, local client machine requirements are minimal:

* **Operating System:** Windows 10/11, macOS, or Linux.
* **Python Runtime:** Python 3.8 or greater.
* **Network Connectivity:** A stable, unrestricted internet connection capable of communicating with Google Cloud endpoints via HTTPS.
* **Core Dependencies:** 
  * `earthengine-api` (Google Earth Engine Python client)
  * `Numpy` (numerical array processing)
  * `Pandas ` (tabular data handling)
  * `scikit-learn` (machine learning - RandomForestRegressor)

---

## Installation Instructions

Follow these steps to set up the execution environment on your local system:

<Sequence>
{/* Reason: Environment setup and GEE authentication requires a strict linear sequence; skipping authentication or initializing out of order causes runtime failures. */}
  <Step title="Clone the Repository" subtitle="Step 1">
    Clone this repository to your local directory using git:
    ```bash
    git clone [https://github.com/your-username/GEE-based-LEAF-Production-Tool.git](https://github.com/your-username/GEE-based-LEAF-Production-Tool.git)
    cd GEE-based-LEAF-Production-Tool
    ```
  </Step>
  <Step title="Configure Environment" subtitle="Step 2">
    Create a clean Python virtual environment and activate it:
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
  </Step>
  <Step title="Install Core Dependencies" subtitle="Step 3">
    Install the official Google Earth Engine client library along with any auxiliary workflow packages:
    ```bash
    pip install earthengine-api
    ```
  </Step>
  <Step title="Authenticate with GEE" subtitle="Step 4">
    Authorize your local machine to interact with your GEE cloud instance. Run the command line tool and follow the browser prompts to log into your approved Google account:
    ```bash
    earthengine authenticate
    ```
  </Step>
</Sequence>

For detailed, operating-system-specific troubleshooting (particularly for deep corporate or academic firewalls under Windows platforms), please refer directly to the comprehensive [User Guide](/docs/user_manual.md).

---

## Citation Information

If you use this software tool, its submodules, or data generated by it in a scientific publication, thesis, or academic report, please cite the following original work:

> *[Placeholder: Insert your primary publication details here]*  
> **Example Format:**  
> Sun, L., et al. (2026). A Hybrid Temporal Compositing Algorithm for Multispectral Surface Reflectance Imagery. *Journal of Remote Sensing / Hydrology Source*. DOI: [Insert DOI Link Here]

---

## Documentation & Development

* **Architecture Overview:** To understand the internal software design, script dependencies, or to modify and update the core pipelines, please review the [Code Architecture Guide](/docs/code_architecture.md).

## How to Contribute
We welcome community enhancements, bug fixes, and documentation improvements. Please review our [CONTRIBUTING.md](CONTRIBUTING.md) guidelines before submitting a Pull Request.

## License
Unless otherwise noted, the source code of this project is covered under Crown Copyright, Government of Canada, and is distributed under the [Apache 2.0 License](LICENSE).

### Trademark & Corporate Identity Notice
The Canada wordmark and related graphics associated with this distribution are protected under international trademark and copyright law. No permission is granted to use them outside the parameters of the Government of Canada's corporate identity program. For explicit guidelines, please refer to the [Federal Identity Requirements](https://www.canada.ca/en/government/system/government-communications/federal-identity-requirements.html).identity-requirements.html).identity-requirements.html).
