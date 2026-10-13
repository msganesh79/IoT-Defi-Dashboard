// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IoTDataOracle
 * @dev Trusted Oracle Smart Contract for IoT telemetry data integrity in DeFi applications.
 * Features automated Circuit Breaker, Oracle authentication, and telemetry audit history.
 */
contract IoTDataOracle {
    // Contract Owner (Admin)
    address public owner;

    // Designated Trusted Oracle Address (Authorized to submit validated data)
    address public trustedOracle;

    // Telemetry State
    int256 public latestAggregatedValue; // Validated median value (e.g., temperature in x10 precision, 255 = 25.5°C)
    uint256 public latestValidNodeCount;   // Number of non-anomalous IoT nodes contributing to this update
    uint256 public lastUpdateTimestamp;   // Block timestamp of latest update
    uint256 public totalUpdateCount;       // Counter of successful updates

    // Circuit Breaker State (Emergency pause for DeFi protection)
    bool public circuitBreakerTripped;
    int256 public minAllowedValue; // Safety floor (e.g., -500 for -50.0°C)
    int256 public maxAllowedValue; // Safety ceiling (e.g., 1000 for 100.0°C)
    int256 public maxAllowedDelta; // Maximum allowed change between consecutive updates (e.g., 300 for 30.0°C jump)

    // Historical record of telemetry updates
    struct TelemetryRecord {
        uint256 timestamp;
        int256 value;
        uint256 validNodeCount;
        uint256 blockNumber;
    }
    TelemetryRecord[] public history;

    // Events
    event DataUpdated(int256 indexed aggregatedValue, uint256 validNodeCount, uint256 timestamp);
    event AnomalyDetected(string reason, int256 offendingValue, uint256 timestamp);
    event CircuitBreakerTripped(string reason, int256 value, uint256 timestamp);
    event CircuitBreakerReset(address indexed admin, uint256 timestamp);
    event OracleAddressUpdated(address indexed oldOracle, address indexed newOracle);
    event SafetyLimitsUpdated(int256 minVal, int256 maxVal, int256 maxDelta);

    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "IoTOracle: Caller is not the contract owner");
        _;
    }

    modifier onlyOracle() {
        require(msg.sender == trustedOracle, "IoTOracle: Caller is not authorized trusted oracle");
        _;
    }

    modifier whenCircuitBreakerNormal() {
        require(!circuitBreakerTripped, "IoTOracle: CIRCUIT BREAKER TRIPPED! Transactions paused for security");
        _;
    }

    /**
     * @dev Constructor initializes owner, trusted oracle, and default safety limits.
     * @param _trustedOracle Address of the Python Oracle engine wallet.
     */
    constructor(address _trustedOracle) {
        require(_trustedOracle != address(0), "IoTOracle: Invalid oracle address");
        owner = msg.sender;
        trustedOracle = _trustedOracle;

        // Default safety parameters (Assuming temperature scale x10: 250 = 25.0°C)
        minAllowedValue = -500;  // -50.0°C
        maxAllowedValue = 1500;  // 150.0°C
        maxAllowedDelta = 400;   // 40.0°C max change per update
        circuitBreakerTripped = false;
    }

    /**
     * @dev Core function called by Python Oracle to record aggregated, validated data.
     * @param _aggregatedValue Validated median sensor value from consensus.
     * @param _validNodeCount Number of healthy IoT nodes that passed Z-score check.
     */
    function updateData(int256 _aggregatedValue, uint256 _validNodeCount) 
        external 
        onlyOracle 
        whenCircuitBreakerNormal 
    {
        require(_validNodeCount > 0, "IoTOracle: Requires at least 1 valid node payload");

        // 1. Safety Bounds Check
        if (_aggregatedValue < minAllowedValue || _aggregatedValue > maxAllowedValue) {
            circuitBreakerTripped = true;
            emit CircuitBreakerTripped("Value exceeds safety floor/ceiling boundaries", _aggregatedValue, block.timestamp);
            emit AnomalyDetected("Out of bounds value received", _aggregatedValue, block.timestamp);
            return;
        }

        // 2. Sudden Delta Jump Check (Skip on first update)
        if (totalUpdateCount > 0) {
            int256 delta = _aggregatedValue > latestAggregatedValue 
                ? _aggregatedValue - latestAggregatedValue 
                : latestAggregatedValue - _aggregatedValue;
            
            if (delta > maxAllowedDelta) {
                circuitBreakerTripped = true;
                emit CircuitBreakerTripped("Extreme rate-of-change jump detected", _aggregatedValue, block.timestamp);
                emit AnomalyDetected("Sudden value spike exceeding max allowed delta", _aggregatedValue, block.timestamp);
                return;
            }
        }

        // 3. Update On-Chain State
        latestAggregatedValue = _aggregatedValue;
        latestValidNodeCount = _validNodeCount;
        lastUpdateTimestamp = block.timestamp;
        totalUpdateCount++;

        // 4. Save to History Audit Log
        history.push(TelemetryRecord({
            timestamp: block.timestamp,
            value: _aggregatedValue,
            validNodeCount: _validNodeCount,
            blockNumber: block.number
        }));

        emit DataUpdated(_aggregatedValue, _validNodeCount, block.timestamp);
    }

    /**
     * @dev Reset circuit breaker state after manual investigation by Admin.
     */
    function resetCircuitBreaker() external onlyOwner {
        circuitBreakerTripped = false;
        emit CircuitBreakerReset(msg.sender, block.timestamp);
    }

    /**
     * @dev Update trusted oracle wallet address.
     */
    function setOracleAddress(address _newOracle) external onlyOwner {
        require(_newOracle != address(0), "IoTOracle: Invalid address");
        emit OracleAddressUpdated(trustedOracle, _newOracle);
        trustedOracle = _newOracle;
    }

    /**
     * @dev Update Circuit Breaker safety parameters.
     */
    function setSafetyLimits(int256 _min, int256 _max, int256 _maxDelta) external onlyOwner {
        require(_min < _max, "IoTOracle: Min must be less than Max");
        minAllowedValue = _min;
        maxAllowedValue = _max;
        maxAllowedDelta = _maxDelta;
        emit SafetyLimitsUpdated(_min, _max, _maxDelta);
    }

    /**
     * @dev Getter for history count.
     */
    function getHistoryCount() external view returns (uint256) {
        return history.length;
    }
}
