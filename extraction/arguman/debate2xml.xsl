<?xml version="1.0" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Match the document's root -->
  <xsl:template match="/">
    <debate>
      <debate-title><xsl:value-of select="//h3/span" /></debate-title>
      <debate-url><xsl:value-of select="//div[@class='share']/a/@href" /></debate-url>
      <debate-author><xsl:value-of select="//div[@class='sender']//a/@href" /></debate-author>

      <!-- Read all arguments from the app div -->
      <premises>
	<xsl:apply-templates select="//div[@id='app']" />
      </premises>
    </debate>
  </xsl:template>


  <!-- Match the general 'app' div -->
  <xsl:template match="div[@id='app']">
    <xsl:apply-templates select="./*/ul" />
  </xsl:template>

  <!-- Match a 'node' in the argument tree -->
  <xsl:template match="ul">
    <xsl:apply-templates select="./li/div[2]" />
  </xsl:template>

  <!-- Match a premise -->
  <xsl:template match="li/div[2]">
    <premise>
      <premise-id><xsl:value-of select="./@data-id" /></premise-id>
      <premise-ref><xsl:value-of select="../../../div[2]/@data-id" /></premise-ref>
      <premise-type><xsl:value-of select="./@data-type" /></premise-type>
      <premise-weight><xsl:value-of select="./@data-weight" /></premise-weight>
      <premise-content><xsl:value-of select="./div[3]" /></premise-content>
      <premise-author><xsl:value-of select=".//div[@class='premise-user']/*/a/@href" /></premise-author>
      <premise-date><xsl:value-of select=".//time/@datetime" /></premise-date>
      <premise-sources>
	<xsl:apply-templates select=".//p[@class='links']/a" />
      </premise-sources>
      <premise-support><xsl:value-of select=".//div[@class='supporters']" /></premise-support>
      <premise-fallacies>
	<xsl:apply-templates select=".//div[@class='fallacy']" />
      </premise-fallacies>
    </premise>
    <xsl:apply-templates select="..//li/div[2]" />
  </xsl:template>

  <!-- Match a premise fallacy block -->
  <xsl:template match="div[@class='fallacy']">
    <fallacy>
      <fallacy-type><xsl:value-of select="./text()" /></fallacy-type>
      <fallacy-reason><xsl:value-of select=".//div[@class='fallacy-reasons']" /></fallacy-reason>
    </fallacy>
  </xsl:template>

  <!-- Match a premise source links block -->
  <xsl:template match="p[@class='links']/a">
    <source><xsl:value-of select="@href" /></source>
  </xsl:template>
  
</xsl:stylesheet>



