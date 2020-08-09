# PCF8574 Decoder

The PCF8574 is a 8 bit I2C I/O Expander

It receives the input from sigrok i2c decoder and then outputs the raw data that has been written


It sends the data to next stack decoder like this:


```python
[
  [ bitvalue, startsample, endsample ], # Repeats 8 times, one for each bit
]

# For example:
[
  [1, 53636, 53656], # Bit 7
  [0, 53616, 53636], # Bit 6
  [0, 53596, 53616], # Bit 5
  [1, 53576, 53596], # Bit 4
  [0, 53556, 53576], # Bit 3
  [0, 53536, 53556], # Bit 2
  [0, 53516, 53536], # Bit 1
  [1, 53496, 53516]  # Bit 0
]
```