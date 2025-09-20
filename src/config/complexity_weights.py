"""
Complexity Scoring Algorithm Weights and Configuration
"""

COMPLEXITY_FACTORS = {
    "technical_keywords_density": {
        "weight": 0.275,
        "description": "Identification and weighting of specialized terminology",
        "high_complexity_keywords": [
            "optimization", "analysis", "simulation", "modeling", "calculation", "algorithm",
            "mathematical", "statistical", "monte carlo", "worst-case", "corner analysis",
            "sensitivity", "tolerance", "derating", "thermal analysis", "EMI", "EMC",
            "signal integrity", "impedance", "transmission line", "high-frequency", "RF",
            "microcontroller", "cortex-m4", "ultra-low power", "power management",
            "connectivity", "embedded", "optimization", "integrated"
            "FPGA", "Xilinx", "Altera", "Intel", "VHDL", "Verilog", "SystemVerilog",
            "synthesis", "place and route", "timing closure", "resource utilization",
            "processor core", "32-bit", "64-bit", "RISC", "pipeline", "cache",
            "three-phase", "motor controller", "PLC interface", "industrial communication",
            "Modbus", "Profibus", "EtherCAT", "DeviceNet", "industrial ethernet",
            "fault-tolerant", "dual-redundant", "CISPR 25", "powertrain", "ECU",
            "IEC 60601", "patient isolation", "4kV test voltage", "medical equipment",
            "biocompatibility", "sterilization", "defibrillation", "patient applied part"
        ]
    },
    "design_constraint_count": {
        "weight": 0.15,
        "description": "Number of simultaneous requirements and limitations",
        "constraint_keywords": [
            "requirement", "constraint", "limit", "specification", "tolerance", "range",
            "minimum", "maximum", "typical", "must", "shall", "requirement", "criteria"
        ]
    },
    "domain_specificity": {
        "weight": 0.225,
        "description": "Level of specialized knowledge required",
        "high_specificity_domains": ["automotive", "medical", "analog_rf", "power_electronics"]
    },
    "calculation_complexity": {
        "weight": 0.15,
        "description": "Mathematical analysis requirements",
        "calculation_keywords": [
            "calculate", "formula", "equation", "derive", "compute", "mathematical",
            "integration", "differentiation", "transfer function", "frequency response",
            "gain", "phase", "stability", "margin", "bandwidth", "efficiency", "evaluate", "analysis"
        ]
    },
    "standards_involvement": {
        "weight": 0.15,
        "description": "Compliance and certification requirements",
        "standards_keywords": [
            "AEC-Q100", "ISO 26262", "IEC 60601", "ASIL", "SIL", "functional safety",
            "compliance", "certification", "qualification", "standard", "regulation",
            "EMC", "EMI", "safety", "medical grade", "automotive grade"
        ]
    },
    "multi_domain_integration": {
        "weight": 0.05,
        "description": "Cross-disciplinary knowledge needs",
        "integration_keywords": [
            "system", "integration", "interface", "communication", "protocol", "co-design",
            "hardware-software", "multi-domain", "cross-functional", "interdisciplinary"
        ]
    }
}

# Scoring thresholds for model routing
COMPLEXITY_THRESHOLDS = {
    "claude_sonnet_4": 0.8,
    "grok_2": 0.6,
    "gpt_4o": 0.4,
    "gpt_4o_mini": 0.0
}
