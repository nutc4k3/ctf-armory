# Sigrok Decoders

Some [sigrok decorders](https://sigrok.org/wiki/Protocol_decoders) compatible with [PulseView](https://sigrok.org/wiki/PulseView)

## Decoders

* [**PCF8574**](pcf8574/README.md)
* [**HD44780**](hd44780/README.md) (Only 4 bit mode, expecting PCF8574 decoder output)

## How to install / use


Copy this folder content to:

* On Linux: `~/.local/share/libsigrokdecode/decoders`
* On Windows: `%ProgramData%\libsigrokdecode\decoders`

And then restart pulseview / sigrok