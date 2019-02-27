# Book_Spider
爬取网络上主要的图书平台
### 遇到的一些问题
- 关于在传递item时候为什么要使用`deepcopy()`
  - 因为所有大分类下面的中分类和小分类是共用同一个item，当item在parse函数中获得大分类，中分类，小分类等字段后将item传递给了parse_list函数，由于scrapy是多线程异步框架，所以在parse_list函数爬取图书详情字段的同时，parse函数会继续爬取新的小分类，这时候会将之前爬取到的小分类覆盖掉。所以为了使已经传递给parse_list的item不受影响，应该将item进行deepcopy，即在内存中开辟一块新的位置，而不是引用之前item的地址。
