# Telescan2Coe

Convert a `.tlscan` file to a `.coe` file with this Python script.

## Instructions

### Run the Script

Ensure your `.tlscan` file is accessible. For example, if your file is on the Desktop and named `54b3r.tlscan`, run:

```sh
python script_file.py C:/Users/User/Desktop/54b3r.tlscan
```

### Locate the Output

The generated `output.coe` file will be saved to your Desktop by default. You can change the output directory and filename in the script if needed.

### Update Config Space

Replace the contents of the `configspace.coe` file in `ip/pcileech_cfgspace.coe` with the content from the `output.coe` file.
