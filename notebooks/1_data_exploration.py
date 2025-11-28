import polars as pl
import os

#%%

data_raw_list = []
for file in os.listdir("data"):
    if file.endswith(".json"):
        data_raw_list.append(pl.read_json(os.path.join("data", file)))
        print(f"Loaded {file}")

#%%



#%%
for post in data_raw_list:
  # 调试输出：schema / dtypes / url 列的前几行
  print("schema:", post.schema)
  print("dtypes:", post.dtypes)
  print("columns:", post.columns)
  print("url column preview:")
  print(post.select(pl.col("url")).head(5))
  # 把 url 列转换为 python list 并打印前 5 个元素以便进一步检查
  vals = post.select(pl.col("url")).to_series().to_list()
  print("first 5 url values (python):", vals[:5])
  # url = post.with_columns(pl.col("url").struct.field("urls").str.replace("https://", ""))
    
#%%

print("Data exploration complete")

#%%