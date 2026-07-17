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


# Landscape Evolution And Forecasting (LEAF) Production Tool

The **Landscape Evolution And Forecasting (LEAF)** production tool is a high-performance geospatial pipeline developed in Python utilizing the **Google Earth Engine (GEE) Python client API (`earthengine-api`)**. 

LEAF enables researchers and developers to efficiently generate high-quality biophysical parameter maps and temporal composite images directly from GEE's massive surface reflectance satellite imagery catalog.

## Key Features

* **Flexible Configuration:** Features a highly customizable input parameter dictionary allowing users to define diverse, tailored production requirements.
* **Seamless Batch Exporting:** Supports robust, asynchronous batch-export workflows delivering outputs directly to either **Google Drive** or **Google Cloud Storage (GCS)**.
* **Hybrid Spatial Scoping:** Processes data using either standard predefined national grids or custom user-defined spatial regions (polygons).

---

## Workflow Overview

The operational logic and processing pipeline of the LEAF production tool are illustrated in the flowchart below:

![LEAF Production Tool Flowchart](/wiki_images/flowchart.png)

---

## Spatial Coverage & Tiling

The tool partitions and processes standard outputs using a systematic tiling framework:
* **Standard Grid:** Outputs are organized into tiles covering a **900 km × 900 km** footprint, adhering strictly to the [CCRS Tile Grid System](/wiki_images/CCRS_tile_grid_system.png).
* **National Scale:** A total of **26 standard tiles** completely encompass the entire Canadian landmass.
* **Custom ROIs:** Users can override the standard grid system by passing a custom polygon geometry to target a specific Region of Interest (ROI).

---

## Product Specifications & Data Formats

LEAF currently supports the generation of **four core biophysical products**. Each generated product tile outputs a separate GeoTIFF file along with two auxiliary context layers: a **Quality Control (QC) map** and an **Acquisition Date map**.

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

## Documentation & Development

* **Installation & Setup:** For step-by-step instructions on setting up your environment on Windows platforms, see the [User Guide](/docs/user_manual.md).
* **Architecture Overview:** To understand the internal design, dependencies, or to modify and update the core pipelines, please review the [Code Architecture Guide](/docs/code_architecture.md).

## How to Contribute
We welcome community enhancements, bug fixes, and documentation improvements. Please review our [CONTRIBUTING.md](CONTRIBUTING.md) guidelines before submitting a Pull Request.

## License
Unless otherwise noted, the source code of this project is covered under Crown Copyright, Government of Canada, and is distributed under the [MIT License](LICENSE).

### Trademark & Corporate Identity Notice
The Canada wordmark and related graphics associated with this distribution are protected under international trademark and copyright law. No permission is granted to use them outside the parameters of the Government of Canada's corporate identity program. For explicit guidelines, please refer to the [Federal Identity Requirements](https://www.canada.ca/en/government/system/government-communications/federal-identity-requirements.html).
