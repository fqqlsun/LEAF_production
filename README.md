## GEE-based LEAF Production Tool
This Landscape Evolution And Forecasting (LEAF) production tool was developed using Python and Google Earth Engine (GEE) Python client API (earthengine-api). It enables users to efficiently generate biophysical parameter maps and temporal composite images from GEE's surface reflectance satellite imagery catalog. The tool features two primary capabilities: (1) a highly flexiable input parameter dictionary that allows users to customize diverse production requirements, and (2) a batch-export mode to output results to either Google Drive or Google Cloud Storage. 

The standard outputs of this tool are organized into tiles, which cover an area of 900km x 900km as per [the CCRS' tile grid system](/wiki_images/CCRS_tile_grid_system.png). In total, there are 26 tiles that encompass the Canadian landmass. However, users also have the option to define a customized polygon to specify a desired spatial area for production. 

This tool currently supports the generation of four types of biophysical products: LAI, fCOVER, fAPAR and Albedo. Each product is associated with a corresponding GeoTiff image in outputs. Additionally, for each tile, there is a QC (Quality Control) map and an acquisition date map. The pixel values of the biophysical maps are stored as 8-bits unsigned integers, with specific rescaling factors applied. For LAI, the rescaling factor is 20, while for the remaining three biophyscal maps, it is 200.

The 8-bits bitmask for the QC map is structured as follows:
   * bit 0: 1 indicates the input is out of range
   * bit 1: 1 represents the output is out of range
   * bit 2, 1 indicates an invalid pixel due to various reasons such as cloud, shadow, snow, ice, water, or saturation.
   * bit 3-7: Correspond to the sensor type code. For Landsat 5, 7, 8, 9, and Sentinel-2, their respective sensor type codes are 40, 56, 64, 72, and 168.

The following figure shows the flowchart of LEAF production tool.
![](/wiki_images/flowchart.png)

For the information on how to set up an environment for running LEAF production tool on Windows platform, please refer to [User Guide](/docs/user_manual.md). To improve or update this tool, please review [code architecture](/docs/code_architecture.md). 

## How to Contribute
See [CONTRIBUTING](CONTRIBUTING.md)
## License
Unless otherwise noted, the source code of this project is covered under Crown Copyright, Government of Canada, and is distributed under the [MIT License](LICENSE).

The Canada wordmark and related graphics associated with this distribution are protected under trademark law and copyright law. No permission is granted to use them outside the parameters of the Government of Canada's corporate identity program. For more information, see [Federal identity requirements](https://www.canada.ca/en/government/system/government-communications/federal-identity-requirements.html).


# GEE-HybridTC (Landscape Evolution And Forecasting - LEAF)

**GEE-HybridTC** is a high-performance, cloud-native temporal compositing pipeline implemented within the **Landscape Evolution And Forecasting (LEAF)** production tool framework. It utilizes a novel hybrid approach to reconstruct clear, gap-free, high-quality biophysical parameter maps and temporal composite images from multi-spectral Earth observation data.

**Crucial Platform Requirement:**  
> ⚠️ **Platform Dependency Notice:** GEE-HybridTC is strictly designed to operate on the Google Earth Engine (GEE) platform via the GEE Python Client API (`earthengine-api`). It is explicitly **not intended to function as a standalone software package** independent of Google's cloud architecture. 

---

## Google Earth Engine (GEE) Access & Compliance

Before deploying or attempting to run this software, please carefully read the following access and legal requirements:

* **User Account Obligation:** Users must independently obtain and maintain their own valid [Google Earth Engine Account](https://earthengine.google.com/). 
* **Terms of Service:** Your utilization of GEE-HybridTC and any subsequent data processing tasks are bound by and governed under [Google's Earth Engine Terms of Service](https://earthengine.google.com/terms/).
* **Data & Platform Disclaimer:** The public release of this source code by the authors **does not grant** users access to the Google Earth Engine infrastructure, compute allocations, or its underlying spatial datasets. Users are completely responsible for managing their own platform permissions, cloud project billing, and data quotas.

---

## Key Features

* **Advanced Hybrid Compositing:** Implements the innovative spline-STL approach for sub-monthly temporal resolution enhancement of satellite imagery.
* **Flexible Configuration:** Features a highly customizable input parameter dictionary allowing users to define diverse, tailored production requirements.
* **Seamless Batch Exporting:** Supports robust, asynchronous batch-export workflows delivering outputs directly to either **Google Drive** or **Google Cloud Storage (GCS)**.
* **Hybrid Spatial Scoping:** Processes data using either standard predefined national grids or custom user-defined spatial regions (polygons).

---

## Workflow Overview

The operational logic and processing pipeline of the LEAF/GEE-HybridTC production tool are illustrated in the flowchart below:

![LEAF/GEE-HybridTC Production Tool Flowchart](/wiki_images/flowchart.png)

---

## Spatial Coverage & Tiling

The tool partitions and processes standard outputs using a systematic tiling framework:
* **Standard Grid:** Outputs are organized into tiles covering a **900 km × 900 km** footprint, adhering strictly to the [CCRS Tile Grid System](/wiki_images/CCRS_tile_grid_system.png).
* **National Scale:** A total of **26 standard tiles** completely encompass the entire Canadian landmass.
* **Custom ROIs:** Users can override the standard grid system by passing a custom polygon geometry to target a specific Region of Interest (ROI).

---

## Product Specifications & Data Formats

The framework currently supports the generation of **four core biophysical products**. Each generated product tile outputs a separate GeoTIFF file along with two auxiliary context layers: a **Quality Control (QC) map** and an **Acquisition Date map**.

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

## System Requirements

Because the heavy computational lifting (pixel-level map algebra and cloud masking) is executed on Google Earth Engine's cloud servers, local client machine requirements are minimal:

* **Operating System:** Windows 10/11, macOS, or Linux.
* **Python Runtime:** Python 3.8 or greater.
* **Network Connectivity:** A stable, unrestricted internet connection capable of communicating with Google Cloud endpoints via HTTPS.
* **Core Dependencies:** 
  * `earthengine-api` (Google Earth Engine Python client)
  * `google-auth` (for account credential handshake)

---

## Installation Instructions

Follow these steps to set up the execution environment on your local system:

<Sequence>
{/* Reason: Environment setup and GEE authentication requires a strict linear sequence; skipping authentication or initializing out of order causes runtime failures. */}
  <Step title="Clone the Repository" subtitle="Step 1">
    Clone this repository to your local directory using git:
    ```bash
    git clone [https://github.com/your-username/GEE-HybridTC.git](https://github.com/your-username/GEE-HybridTC.git)
    cd GEE-HybridTC
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

## Known Limitations

While GEE-HybridTC is a robust production tool, users should be aware of the following operational constraints:
* **GEE Quota Limits:** Large batch processing exports spanning multiple years or massive custom regions may occasionally encounter Earth Engine memory ceilings (`User memory limit exceeded`) or user rate-limiting constraints. Users can mitigate this by chunking their runs into smaller temporal or spatial subsets.
* **Persistent Persistent Cloud Cover:** In sub-polar or intensely cloud-dominated macroclimates where zero clear-sky satellite inputs are recorded across entire seasons, the underlying spline-STL interpolation algorithms may exhibit higher uncertainty or default to flag pixels as invalid within the QC layer.
* **Sensor-Specific Calibration:** Minor discrepancies in biophysical product cross-calibration may occur at transition edges where data streams blend between older sensors (e.g., Landsat 5) and newer architectures (e.g., Sentinel-2).

---

## Citation Information

If you use this software tool, the underlying `HybridTC` algorithm, or data generated by it in a scientific publication, thesis, or academic report, please cite the following original work:

> *[Placeholder: Insert your primary publication details here]*  
> **Example Format:**  
> Sun, L., et al. (2026). A Hybrid Temporal Compositing Algorithm for Multispectral Surface Reflectance Imagery. *Journal of Remote Sensing / Hydrology Source*. DOI: [Insert DOI Link Here]

---

## Documentation & Development

* **Architecture Overview:** To understand the internal software design, script dependencies, or to modify and update the core pipelines, please review the [Code Architecture Guide](/docs/code_architecture.md).

## How to Contribute
We welcome community enhancements, bug fixes, and documentation improvements. Please review our [CONTRIBUTING.md](CONTRIBUTING.md) guidelines before submitting a Pull Request.

## License
Unless otherwise noted, the source code of this project is covered under Crown Copyright, Government of Canada, and is distributed under the [MIT License](LICENSE).

### Trademark & Corporate Identity Notice
The Canada wordmark and related graphics associated with this distribution are protected under international trademark and copyright law. No permission is granted to use them outside the parameters of the Government of Canada's corporate identity program. For explicit guidelines, please refer to the [Federal Identity Requirements](https://www.canada.ca/en/government/system/government-communications/federal-identity-requirements.html).identity-requirements.html).
