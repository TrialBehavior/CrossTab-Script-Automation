import pyreadstat
df, meta = pyreadstat.read_sav(r"C:\Users\EthanTran\OneDrive - Trial Behavior Consulting\Desktop\automating_spss\pdf_testing\Q4\Untitled2.sav")
# Access metadata
print(meta.column_names_to_labels)