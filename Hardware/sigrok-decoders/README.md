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

![](https://user-images.githubusercontent.com/578310/89724821-25e5b680-d9de-11ea-8ab9-1c9dd7dd2ee9.png)
![](https://user-images.githubusercontent.com/578310/89724830-34cc6900-d9de-11ea-8c07-2e7f5bd64a8b.png)
